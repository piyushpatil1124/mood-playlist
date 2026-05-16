import random
from dataclasses import dataclass
from typing import Optional
from .mood_engine import MoodVector, TimeBlock, DayArc


@dataclass
class Track:
    title: str
    artist: str
    album: str
    duration_sec: int
    mood_vec: MoodVector
    genre: str
    block_affinity: list
    icon: str = "🎵"

    @property
    def duration_str(self):
        m, s = divmod(self.duration_sec, 60)
        return f"{m}:{s:02d}"

    def score_for(self, target):
        return 100 - self.mood_vec.distance(target)


CATALOG = [
    Track("Golden Hour Drift", "Nils Frahm",      "All Melody",         222, MoodVector(72,66,32,70), "Ambient",         ["morning","noon"],  "🌅"),
    Track("First Light",       "Bonobo",           "Black Sands",        255, MoodVector(68,72,28,65), "Electronic",      ["morning"],         "🌤"),
    Track("Morning Pulse",     "Caribou",          "Swim",               238, MoodVector(78,70,30,75), "Psychedelic",     ["morning","focus"], "☀️"),
    Track("Awaken",            "Olafur Arnalds",   "Re:member",          302, MoodVector(55,60,55,50), "Neo-Classical",   ["morning","wind"],  "🌿"),
    Track("Daybreak",          "Sigur Ros",        "Agaetis byrjun",     380, MoodVector(50,65,65,40), "Post-Rock",       ["morning","wind"],  "🌄"),
    Track("Neural Pathways",   "Tycho",            "Epoch",              268, MoodVector(80,68,58,78), "Electronic",      ["focus"],           "🧠"),
    Track("Deep Work State",   "Four Tet",         "There Is Love",      371, MoodVector(82,65,62,80), "Electronic",      ["focus"],           "💡"),
    Track("Clarity Engine",    "Jon Hopkins",      "Immunity",           344, MoodVector(85,62,60,85), "Electronic",      ["focus","burst"],   "⚙️"),
    Track("The Zone",          "Bicep",            "Bicep",              292, MoodVector(88,70,40,88), "Electronic",      ["focus","burst"],   "🎯"),
    Track("Systemic",          "Floating Points",  "Elaenia",            320, MoodVector(75,64,68,72), "Jazz-Electronic", ["focus"],           "🔬"),
    Track("Midday Sunbeam",    "Mac Ayres",        "Easy",               213, MoodVector(68,82,22,65), "R&B",             ["noon"],            "🌞"),
    Track("Floatin",           "Rex Orange County","Apricot Princess",   198, MoodVector(65,85,20,62), "Indie Pop",       ["noon"],            "🎈"),
    Track("Cottonwood",        "Still Woozy",      "Lately",             178, MoodVector(70,88,18,68), "Indie Pop",       ["noon","morning"],  "🌾"),
    Track("Bloom Again",       "Novo Amor",        "Birthplace",         247, MoodVector(58,76,42,52), "Indie Folk",      ["noon","wind"],     "🌸"),
    Track("Easy Wind",         "Khruangbin",       "Con Todo El Mundo",  280, MoodVector(55,80,35,52), "Soul",            ["noon"],            "🌬"),
    Track("Underwater Hours",  "Bibio",            "Ambivalence Ave.",   321, MoodVector(38,55,65,38), "Lo-fi",           ["slump"],           "🌊"),
    Track("Slow Dissolve",     "Washed Out",       "Within and Without", 264, MoodVector(40,58,62,38), "Chillwave",       ["slump","wind"],    "🫧"),
    Track("Drift Current",     "Com Truise",       "Iteration",          309, MoodVector(42,52,58,45), "Synthwave",       ["slump"],           "🌀"),
    Track("Afternoon Haze",    "Tame Impala",      "Currents",           235, MoodVector(45,60,55,48), "Psych-Rock",      ["slump"],           "🎆"),
    Track("Poolside Fog",      "Mild High Club",   "Skiptracing",        200, MoodVector(35,62,48,38), "Lo-fi Jazz",      ["slump","noon"],    "☁️"),
    Track("Ignition Sequence", "RUFUS DU SOL",     "Bloom",              288, MoodVector(90,72,35,90), "Electronic",      ["burst"],           "🔥"),
    Track("Surge",             "Fred Again",       "Actual Life",        219, MoodVector(88,76,30,88), "Electronic",      ["burst"],           "⚡"),
    Track("Peak Hours",        "Bicep",            "Isles",              317, MoodVector(92,68,40,92), "Electronic",      ["burst"],           "🏔"),
    Track("Blood Rush",        "Moderat",          "III",                263, MoodVector(85,62,50,85), "Electronic",      ["burst","focus"],   "💥"),
    Track("Body Weight",       "Caribou",          "Suddenly",           240, MoodVector(80,75,30,82), "Electronic",      ["burst","noon"],    "🌊"),
    Track("Vespers",           "Brian Eno",        "Music for Airports", 392, MoodVector(22,48,82,28), "Ambient",         ["wind"],            "🌙"),
    Track("Stargazing Pt II",  "Tycho",            "Dive",               308, MoodVector(35,55,70,32), "Ambient",         ["wind"],            "✨"),
    Track("Night Petals",      "Olafur Arnalds",   "Some Kind of Peace", 291, MoodVector(30,50,78,28), "Neo-Classical",   ["wind"],            "🌺"),
    Track("Sleep Story",       "Nils Frahm",       "Felt",               434, MoodVector(18,42,88,20), "Neo-Classical",   ["wind"],            "💤"),
    Track("Fade to Blue",      "Tycho",            "Simulcast",          265, MoodVector(28,52,72,28), "Ambient",         ["wind","slump"],    "🫐"),
]


class PlaylistGenerator:
    def __init__(self, catalog=None):
        self.catalog = catalog or CATALOG

    def generate(self, arc, tracks_per_block=4, preferred_genres=None, seed=None):
        if seed is not None:
            random.seed(seed)
        result = []
        for block in arc.enabled_blocks():
            target = block.adjusted_mood(arc.global_mood)
            candidates = self._candidates_for(block, preferred_genres)
            scored = sorted(candidates, key=lambda t: -t.score_for(target))
            top = scored[:max(tracks_per_block * 2, 6)]
            chosen = random.sample(top, min(tracks_per_block, len(top)))
            chosen.sort(key=lambda t: -t.score_for(target))
            for t in chosen:
                result.append((t, block))
        return result

    def _candidates_for(self, block, preferred_genres=None):
        pool = [t for t in self.catalog if block.id in t.block_affinity]
        if not pool:
            pool = self.catalog[:]
        if preferred_genres:
            filtered = [t for t in pool if t.genre in preferred_genres]
            if filtered:
                pool = filtered
        return pool

    def total_duration(self, playlist):
        total = sum(t.duration_sec for t, _ in playlist)
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        return f"{h}h {m}m" if h else f"{m}m {s}s"