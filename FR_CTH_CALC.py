from small_guns import small_guns
from big_guns import big_guns
from energy_weapons import energy_weapons
from ammo import ammo
from armor import armor
from headgear import headgear

all_weapons =  {**small_guns, **big_guns, **energy_weapons}

# Define parameters
SKILL = 300
PERCEPTION = 5
STRENGTH = 6
WEAPON_NAME = "Wattz 2000 Laser Rifle"  # This should be a valid weapon name from one of the weapon dictionaries
AMMO_TYPE = "Micro Fusion Cell"  # This should be a valid ammo type from the ammo dictionary
TARGET_DISTANCE = 40
IS_SHARPSHOOTER = False
WEAPON_HANDLING = False
WEAPON_CRAFTING_BONUS = 0
IS_BLIND = False
DEFENDER_AGILITY = 5
DEFENDER_LIVEWIRE = False
DEFENDER_ARMOR = "Combat Armor"  # This will be the name of the armor from the list
DEFENDER_HEADGEAR = "Combat Helmet"  # This will be the name of the headgear from the list
DEFENDER_DODGER_RANK = 0  # 0 for no perk, 1 for first rank, 2 for second rank
DEFENDER_IN_YOUR_FACE = True
AIMED_BODY_PART = 'Eyes'  # Can be None, 'Eyes', 'Head', 'Groin', 'Arm', 'Leg', or 'Torso'
IS_ONE_HANDER = False
ATTACK_TYPE = "Burst"

# Aimed attack data
AIMED_ATTACK_DATA = {
    'Eyes':  {'hit_penalty': 60},
    'Head':  {'hit_penalty': 40},
    'Groin': {'hit_penalty': 30},
    'Arm':  {'hit_penalty': 30},
    'Leg':  {'hit_penalty': 20},
    'Torso': {'hit_penalty': 0}
}

def calculate_sight_range(perception, is_blind, is_sharpshooter):
    if is_blind:
        return 23  # Blindness limits sight range to 23 regardless of Perception
    base_range = 23 + (perception - 1) * 3
    sharpshooter_bonus = 6 if is_sharpshooter else 0
    return base_range + sharpshooter_bonus

def calculate_defender_ac(DEFENDER_AGILITY, DEFENDER_LIVEWIRE, DEFENDER_ARMOR, DEFENDER_HEADGEAR, AIMED_BODY_PART):
    if DEFENDER_LIVEWIRE:
        base_ac = 6 * DEFENDER_AGILITY  # Double the Agility bonus if Livewire is True
    else:
        base_ac = 3 * DEFENDER_AGILITY  # Normal Agility bonus

    if AIMED_BODY_PART in ["Eyes", "Head"]:
        armor_ac = headgear.get(DEFENDER_HEADGEAR, 0)
    else:
        armor_ac = armor.get(DEFENDER_ARMOR, 0)

    total_ac = base_ac + armor_ac
    return min(total_ac, 140)  # AC is capped at 140


def calculate_hit_chance(skill, perception, strength, weapon, ammo_type, target_distance, 
                         is_sharpshooter, aimed_body_part, weapon_handling, weapon_crafting_bonus, 
                         defender_dodger_rank, defender_in_your_face,
                         defender_agility, defender_livewire, defender_armor, defender_headgear,
                         is_blind, attack_type, is_one_hander):
    
    # Use the weapon object directly
    weapon_req_st = weapon['st']
    
    # Handle different range formats
    if isinstance(weapon['range'], dict):
        if attack_type == 'Burst':
            weapon_range = weapon['range'].get('B', weapon['range'].get('S', 0))
        else:
            weapon_range = weapon['range'].get('S', 0)
    else:
        weapon_range = weapon['range']
    
    is_accurate = "Accurate" in weapon['perks']
    is_scoped = "Scoped" in weapon['perks']
    is_long_range = "Long Range" in weapon['perks']
    
    # Check for out of range and sight conditions
    sight_range = calculate_sight_range(perception, is_blind, is_sharpshooter)
    
    if target_distance > weapon_range and target_distance > sight_range:
        return "Out of Range & Sight"
    elif target_distance > weapon_range:
        return "Out of Range"
    elif target_distance > sight_range:
        return "Out of Sight"

    # Get ammo characteristics
    ammo_data = ammo[ammo_type]
    ac_mod = ammo_data['ac_mod']

    hit_chance = skill

    # Apply One Hander trait effects (add this block)
    if is_one_hander:
        if weapon['hands'] == 1:
            hit_chance += 20  # +20% for single-handed weapons
        elif weapon['hands'] == 2:
            hit_chance -= 40  # -40% for two-handed weapons

    # Adjust perception for blindness
    if is_blind:
        perception = 1

    # Perception bonus
    if is_scoped:
        if target_distance > 4:
            hit_chance += (perception - 2) * 20
        else:
            hit_chance += 0  # No perception bonus for scoped weapons when target is 4 hexes away or closer
    elif is_long_range:
        hit_chance += (perception - 2) * 16
    else:
        hit_chance += (perception - 2) * 8

    # Sharpshooter perk
    if is_sharpshooter:
        hit_chance += 8

    # Accurate weapon
    if is_accurate:
        hit_chance += 20

    # Distance penalty
    hit_chance -= 4 * target_distance

    # Strength requirement penalty
    strength_penalty = max(0, (weapon_req_st - (2 if weapon_handling else 0)) - strength) * 20
    hit_chance -= strength_penalty

    # Calculate defender's AC
    defender_ac = calculate_defender_ac(defender_agility, defender_livewire, defender_armor, defender_headgear, aimed_body_part)
    
    # Apply AC penalty
    hit_chance -= max(0, defender_ac - ac_mod)

    # Aimed attack penalty
    if aimed_body_part in AIMED_ATTACK_DATA:
        hit_chance -= AIMED_ATTACK_DATA[aimed_body_part]['hit_penalty']

    # Crafting bonuses
    hit_chance += int(weapon_crafting_bonus)

    # Apply Dodger perk effect
    if defender_dodger_rank > 0:
        dodger_reduction = 5 * defender_dodger_rank
        hit_chance -= dodger_reduction
    
    # Clamp hit chance between 5% and 95%
    hit_chance = max(5, min(95, hit_chance))

    # Apply In Your Face perk effect
    if defender_in_your_face and target_distance <= 2:
        hit_chance = min(hit_chance, 50)

    return f"{round(hit_chance)}%"

def main():
    weapon = all_weapons.get(WEAPON_NAME)
    if not weapon:
        print(f"Error: Invalid weapon '{WEAPON_NAME}'")
        return

    result = calculate_hit_chance(
        SKILL, PERCEPTION, STRENGTH, weapon, AMMO_TYPE, TARGET_DISTANCE,
        IS_SHARPSHOOTER, AIMED_BODY_PART, WEAPON_HANDLING, WEAPON_CRAFTING_BONUS,
        DEFENDER_DODGER_RANK, DEFENDER_IN_YOUR_FACE,
        DEFENDER_AGILITY, DEFENDER_LIVEWIRE, DEFENDER_ARMOR, DEFENDER_HEADGEAR,
        IS_BLIND, ATTACK_TYPE, IS_ONE_HANDER
    )
    
    if isinstance(result, str):
        print(f"Hit chance: {result}")
    else:
        print(f"Hit chance: {result}%")
    
    defender_ac = calculate_defender_ac(DEFENDER_AGILITY, DEFENDER_LIVEWIRE, DEFENDER_ARMOR, DEFENDER_HEADGEAR, AIMED_BODY_PART)
    print(f"Defender's AC: {defender_ac}")

if __name__ == "__main__":
    main()

