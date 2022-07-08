from dataclasses import dataclass


@dataclass
class CharacterInfo:
    char_id: int
    name: str


Justinian = CharacterInfo(char_id=0, name="Justinian")
Heraclius = CharacterInfo(char_id=1, name="Heraclius")
Phocas = CharacterInfo(char_id=2, name="Phocas")
Khusrow = CharacterInfo(char_id=3, name="Khusrow")
