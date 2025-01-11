from pydantic_xml import element

from pydantic_adobe_audition.model.session.tracks.audio.audio_clip import AudioClip
from pydantic_adobe_audition.model.session.tracks.common import BaseTrack
from pydantic_adobe_audition.model.session.tracks.common.effects_rack import EffectsRack


class AudioTrack(BaseTrack, tag="audioTrack"):
    effects_rack: EffectsRack | None = element(default=None)
    clips: list[AudioClip] = element(default_factory=list)
