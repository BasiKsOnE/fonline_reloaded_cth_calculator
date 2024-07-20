from flask import Flask, render_template, request, jsonify
from small_guns import small_guns
from big_guns import big_guns
from energy_weapons import energy_weapons
from ammo import ammo
from armor import armor
from headgear import headgear
from FR_CTH_CALC import calculate_hit_chance, calculate_defender_ac

app = Flask(__name__)

# Combine all weapons into one dictionary
all_weapons = {**small_guns, **big_guns, **energy_weapons}

@app.route('/')
def index():
    return render_template('index.html', 
                           weapons=all_weapons, 
                           ammo_types=list(ammo.keys()),
                           armor_types=list(armor.keys()),
                           headgear_types=list(headgear.keys()))

@app.route('/get_valid_ammo/<weapon_name>')
def get_valid_ammo(weapon_name):
    weapon = all_weapons.get(weapon_name)
    if not weapon:
        return jsonify([])
    valid_ammo = weapon.get('ammo', [])
    return jsonify(valid_ammo)

@app.route('/get_valid_attack_types/<weapon_name>')
def get_valid_attack_types(weapon_name):
    weapon = all_weapons.get(weapon_name)
    if not weapon:
        return jsonify([])
    valid_attack_types = weapon.get('attack_types', [])
    return jsonify(valid_attack_types)
    
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    
    weapon = all_weapons.get(data['weapon'])
    if not weapon:
        return jsonify({'hit_chance': "Error: Invalid weapon", 'defender_ac': "N/A"})

    result = calculate_hit_chance(
        skill=int(data['weapon_skill']),
        perception=int(data['perception']),
        strength=int(data['strength']),
        weapon=weapon,
        ammo_type=data['ammo'],
        target_distance=int(data['target_distance']),
        is_sharpshooter=data['sharpshooter'],
        aimed_body_part=data['aimed_body_part'],
        weapon_handling=data['weapon_handling'],
        weapon_crafting_bonus=int(data['weapon_crafting_bonus']),
        defender_dodger_rank=int(data['dodger_rank']),
        defender_in_your_face=data['in_your_face'],
        defender_agility=int(data['defender_agility']),
        defender_livewire=data['livewire'],
        defender_armor=data['armor'],
        defender_headgear=data['headgear'],
        is_blind=data['eye_damage'],
        attack_type=data['attack_type'],
        is_one_hander=data['is_one_hander']
    )

    defender_ac = calculate_defender_ac(
        DEFENDER_AGILITY=int(data['defender_agility']),
        DEFENDER_LIVEWIRE=data['livewire'],
        DEFENDER_ARMOR=data['armor'],
        DEFENDER_HEADGEAR=data['headgear'],
        AIMED_BODY_PART=data['aimed_body_part']
    )
    
    return jsonify({'hit_chance': result, 'defender_ac': defender_ac})

if __name__ == '__main__':
    app.run(debug=True)
