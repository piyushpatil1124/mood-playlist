from dataclasses import dataclass
import math

@dataclass
class MoodVector:
    energy: float
    valence: float
    depth: float
    tempo: float

    def blend(self, other, weight=0.5):
        w = max(0.0, min(1.0, weight))
        return MoodVector(
            energy=self.energy * w + other.energy * (1 - w),
            valence=self.valence * w + other.valence * (1 - w),
            depth=self.depth * w + other.depth * (1 - w),
            tempo=self.tempo * w + other.tempo * (1 - w),
        )

    def distance(self, other):
        return math.sqrt(
            (self.energy - other.energy) ** 2 +
            (self.valence - other.valence) ** 2 +
            (self.depth - other.depth) ** 2 +
            (self.tempo - other.tempo) ** 2
        )

    def to_label(self):
        if self.energy > 70 and self.valence > 60:
            return "Euphoric"
        if self.energy > 70 and self.valence < 40:
            return "Intense"
        if self.energy < 40 and self.valence > 60:
            return "Serene"
        if self.energy < 40 and self.valence < 40:
            return "Melancholic"
        if self.depth > 65:
            return "Introspective"
        if self.tempo > 70:
            return "Driving"
        return "Balanced"


@dataclass
class TimeBlock:
    id: str
    name: str
    time_range: str
    icon: str
    base_mood: MoodVector
    enabled: bool = True

    def adjusted_mood(self, global_vector, influence=0.35):
        return self.base_mood.blend(global_vector, 1 - influence)


class DayArc:
    DEFAULT_BLOCKS = [
        TimeBlock("morning", "Morning Rise",  "6-9 AM",    "🌅", MoodVector(75, 65, 30, 72)),
        TimeBlock("focus",   "Deep Focus",    "9 AM-12 PM","🎯", MoodVector(85, 70, 55, 80)),
        TimeBlock("noon",    "Midday Flow",   "12-2 PM",   "☀️", MoodVector(70, 80, 25, 68)),
        TimeBlock("slump",   "Afternoon Dip", "2-4 PM",    "🌊", MoodVector(40, 55, 60, 42)),
        TimeBlock("burst",   "Evening Burst", "4-7 PM",    "⚡", MoodVector(90, 72, 35, 90)),
        TimeBlock("wind",    "Wind Down",     "7-10 PM",   "🌙", MoodVector(30, 45, 75, 35)),
    ]

    def __init__(self):
        import copy
        self.blocks = copy.deepcopy(self.DEFAULT_BLOCKS)
        self.global_mood = MoodVector(70, 65, 50, 75)

    def enable(self, *block_ids):
        ids = set(block_ids)
        for b in self.blocks:
            b.enabled = b.id in ids

    def enabled_blocks(self):
        return [b for b in self.blocks if b.enabled]

    def dominant_mood(self):
        blocks = self.enabled_blocks()
        if not blocks:
            return self.global_mood
        return MoodVector(
            energy=sum(b.adjusted_mood(self.global_mood).energy for b in blocks) / len(blocks),
            valence=sum(b.adjusted_mood(self.global_mood).valence for b in blocks) / len(blocks),
            depth=sum(b.adjusted_mood(self.global_mood).depth for b in blocks) / len(blocks),
            tempo=sum(b.adjusted_mood(self.global_mood).tempo for b in blocks) / len(blocks),
        )