
from .Extension import Extension
import os,uuid
from pathlib import Path
from pydub import AudioSegment
from midi2audio import FluidSynth
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo


# 拓展的配置信息，用于ai理解拓展的功能 *必填* 
ext_config:dict = {
    "name": "makemidi",   # 拓展名称，用于标识拓展
    "arguments": {
        'midi': 'str',  # 需要转换的文本
    },
    # 拓展的描述信息，用于提示ai理解拓展的功能 *必填* 尽量简短 使用英文更节省token
    "description": "You can use the midi extension to compose music, which only supports numbered musical notation. Use + to raise an octave, - to lower an octave, ~ to sustain a note, _ for a half-step, and . for a dotted note. Multiple symbols can be stacked and separated by spaces. Use # to raise a half-step and b to lower a half-step. Use 0 for a rest. The order does not matter. The instrument code refers to the MIDI instrument list. Not all instruments are available, 0 is the grand piano. The BPM is generally 120, and the key is generally C. Add m for minor key. For example: C C# C#m Cb Cm. To use it: [instrument code] [BPM] [key] [simplified notation]. For example: /#makemidi&0 120 C 3 5 6 1+ 2+~ 1+ 2+ 3+~ 1+ 6 5 3 1+ 2+ 6~#/",
    # 参考词，用于上下文参考使用，为空则每次都会被参考(消耗token)
    "refer_word": [],
    # 作者信息
    "author": "CCYellowStar",
    # 版本
    "version": "0.0.1",
    # 拓展简介
    "intro": "让ai输入midi生成简易midi音乐",
}


# 自定义扩展
class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        """ 当拓展被调用时执行的函数 *由拓展自行实现*
        
        参数:
            arg_dict: dict, 由ai解析的参数字典 {参数名: 参数值}
        """
        custom_config:dict = self.get_custom_config()  # 获取yaml中的配置信息
        
        current_path = "resources"
        midi_path = f"{current_path}/midi"

        # 获取参数
        midi_text = str(arg_dict.get('midi', None))
        arg = str(midi_text)               

        def signature(key_signature, note, tone_change):
            if key_signature == 'C' or key_signature == 'Am':
                pass
            elif key_signature == 'G' or key_signature == 'Em':
                tones = [5, 6, 7, 1, 2, 3, 4]
                note = tones[note - 1]
                if note == 4:
                    tone_change += 1
            elif key_signature == 'F' or key_signature == 'Dm':
                tones = [4, 5, 6, 7, 1, 2, 3]
                note = tones[note - 1]
                if note == 7:
                    tone_change -= 1
            elif key_signature == 'D' or key_signature == 'Bm':
                tones = [2, 3, 4, 5, 6, 7, 1]
                note = tones[note - 1]
                if note == 1 or note == 4:
                    tone_change += 1
            elif key_signature == 'Bb' or key_signature == 'Gm':
                tones = [7, 1, 2, 3, 4, 5, 6]
                note = tones[note - 1]
                if note == 7 or note == 3:
                    tone_change -= 1
            elif key_signature == 'A' or key_signature == 'F#m':
                tones = [6, 7, 1, 2, 3, 4, 5]
                note = tones[note - 1]
                if note == 1 or note == 4 or note == 5:
                    tone_change += 1
            elif key_signature == 'Eb' or key_signature == 'Cm':
                tones = [3, 4, 5, 6, 7, 1, 2]
                note = tones[note - 1]
                if note == 7 or note == 3 or note == 6:
                    tone_change -= 1
            elif key_signature == 'E' or key_signature == 'C#m':
                tones = [3, 4, 5, 6, 7, 1, 2]
                note = tones[note - 1]
                if note == 1 or note == 4 or note == 5 or note == 2:
                    tone_change += 1
            elif key_signature == 'Ab' or key_signature == 'Fm':
                tones = [6, 7, 1, 2, 3, 4, 5]
                note = tones[note - 1]
                if note == 7 or note == 3 or note == 6 or note == 2:
                    tone_change -= 1
            elif key_signature == 'B' or key_signature == 'G#m' or key_signature == 'Cb':
                tones = [7, 1, 2, 3, 4, 5, 6]
                note = tones[note - 1]
                if note == 1 or note == 4 or note == 5 or note == 2 or note == 6:
                    tone_change += 1
            elif key_signature == 'C#' or key_signature == 'Db' or key_signature == 'A#m' or key_signature == 'Bbm':
                tones = [1, 2, 3, 4, 5, 6, 7]
                note = tones[note - 1]
                tone_change += 1
            elif key_signature == 'F#' or key_signature == 'D#m' or key_signature == 'Gb':
                tones = [4, 5, 6, 7, 1, 2, 3]
                note = tones[note - 1]
                if note != 7:
                    tone_change += 1
            else:
                pass
            return note, tone_change


        def parser_notes(note, key_signature):
            if '~' in note:
                length = 1 + int(str(note).count('~'))
                note = note.replace('~', '')
            elif '_' in note:
                length = 1 * 0.5 ** int(str(note).count('_'))
                note = note.replace('_', '')
            elif '.' in note:
                length = 1 + 0.5 * int(str(note).count('.'))
                note = note.replace('.', '')
            else:
                length = 1
            if '#' in note:
                tone_change = 1
                note = note.replace('#', '')
            elif 'b' in note:
                tone_change = -1
                note = note.replace('b', '')
            else:
                tone_change = 0
            if '+' in note:
                base_sum = int(str(note).count('+'))
                note = int(note.replace('+', ''))
            elif '-' in note:
                base_sum = -int(str(note).count('-'))
                note = int(note.replace('-', ''))
            else:
                note = int(note)
                base_sum = 0
            # 小调
            if 'm' in key_signature:
                if note == 3 or note == 6 or note == 7:
                    tone_change -= 1

            return note, length, tone_change, base_sum


        def play_note(note, length, track, bpm=120, base_num=0, delay=0, velocity=1.0, channel=0, tone_change=0):
            meta_time = 60 * 60 * 10 / bpm
            major_notes = [0, 2, 2, 1, 2, 2, 2, 1]
            base_note = 60
            if note != 0 and 1 <= note <= 7:
                if tone_change == 0:
                    note = base_note + base_num * 12 + sum(major_notes[0:note])
                elif tone_change > 0:
                    note = base_note + base_num * 12 + sum(major_notes[0:note]) + tone_change
                elif tone_change < 0:
                    note = base_note + base_num * 12 + sum(major_notes[0:note]) + tone_change
                track.append(
                    Message('note_on', note=note, velocity=round(64 * velocity),
                            time=round(delay * meta_time), channel=channel))
                track.append(
                    Message('note_off', note=note, velocity=round(64 * velocity),
                            time=round(meta_time * length), channel=channel))
            elif note == 0:
                track.append(
                    Message('note_on', note=note, velocity=round(64 * velocity),
                            time=round(delay * meta_time), channel=channel))
                track.append(
                    Message('note_off', note=note, velocity=round(64 * velocity),
                            time=round(meta_time * length), channel=channel))


        def make_midi(uuid, notes, bpm=120, program=0, key_signature='C'):
            if os.path.exists(midi_path):
                pass
            else:
                os.mkdir(midi_path)
            try:
                os.remove(f'{midi_path}/{uuid}.mid')
                os.remove(f'{midi_path}/{uuid}.wav')
            except:
                pass
            mid = MidiFile()
            track = MidiTrack()
            mid.tracks.append(track)
            tempo = bpm2tempo(bpm)
            track.append(Message('program_change', channel=0, program=program, time=0))
            track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
            track.append(MetaMessage('key_signature', key=key_signature))
            for note in notes:
                note, length, tone_change, base_sum = parser_notes(note, key_signature)
                note, tone_change = signature(key_signature, note, tone_change)
                play_note(note, length, track, bpm, base_sum, tone_change=tone_change)

            mid.save(f'{midi_path}/{uuid}.mid')
            midi2wav(uuid)
            high_volume(uuid)
            file_name = f"{midi_path}/{uuid}.wav"
            return f"file:///{os.path.abspath(file_name)}"


        def multi_tracks(uuid, tracks, bpm=120, key_signature='C'):
            if os.path.exists(midi_path):
                pass
            else:
                os.mkdir(midi_path)
            try:
                os.remove(f'{midi_path}/{uuid}.mid')
                os.remove(f'{midi_path}/{uuid}.wav')
            except:
                pass
            mid = MidiFile(type=1)
            tempo = bpm2tempo(bpm)
            for simple in tracks:
                if simple[0] == ' ':
                    simple = simple[1:]
                channel = int(simple.split()[0])
                program = int(simple.split()[1])
                velocity = float(simple.split()[2])
                notes = simple.split()[3:]
                track = MidiTrack()
                mid.tracks.append(track)
                track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
                track.append(MetaMessage('key_signature', key=key_signature))
                track.append(Message('program_change', channel=channel, program=program, time=0))
                for note in notes:
                    note, length, tone_change, base_sum = parser_notes(note, key_signature)
                    note, tone_change = signature(key_signature, note, tone_change)
                    play_note(note, length, track, bpm, base_sum, tone_change=tone_change, channel=channel, velocity=velocity)

            mid.save(f'{midi_path}/{uuid}.mid')
            midi2wav(uuid)
            high_volume(uuid)
            file_name = f"{midi_path}/{uuid}.wav"
            return f"file:///{os.path.abspath(file_name)}"


        def midi2wav(uuid):
            sf_path = f'{current_path}/gm.sf2'
            s = FluidSynth(sound_font=sf_path)
            s.midi_to_audio(f'{midi_path}/{uuid}.mid', f'{midi_path}/{uuid}.wav')


        def high_volume(uuid):
            song = AudioSegment.from_wav(f'{midi_path}/{uuid}.wav')
            song = song + 20
            song.export(f'{midi_path}/{uuid}.wav', format="wav")

        if '>' not in arg:
            arg = arg.split()
            program = int(arg[0])
            bpm = int(arg[1])
            key_signature = arg[2]
            notes = arg[3:]
            try:
                result = make_midi(uuid.uuid1(), notes, program=program, bpm=bpm, key_signature=key_signature)
                return {
                    'voice': result,             # 语音url
                    'text': f"[midi生成]{midi_text}",    # 文本
                }
            except Exception as e:
                return {'text': f'[ext_makemidi]编曲失败，参数错误：{e}'}
        else:
            arg = arg.replace('\n', '').split('>')
            bpm = int(arg[0].split()[0])
            key_signature = arg[0].split()[1]
            tracks = arg[1:]
            try:
                result = multi_tracks(uuid.uuid1(), tracks, bpm=bpm, key_signature=key_signature)
                return {
                    'voice': result,             # 语音url
                    'text': f"[midi生成]{midi_text}",    # 文本
                }
            except Exception as e:
                return {'text': f'[ext_makemidi]编曲失败，参数错误：{e}'}

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
