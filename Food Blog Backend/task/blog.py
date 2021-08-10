import sqlite3
import argparse


def kreiraj_tabele():
    global conn
    global cur
    db_name = args.food_blog
    conn = sqlite3.connect(db_name, uri=True)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS meals(meal_id INTEGER PRIMARY KEY, \
                meal_name TEXT UNIQUE NOT NULL)")
    conn.commit()
    cur.execute("CREATE TABLE IF NOT EXISTS ingredients(ingredient_id INTEGER PRIMARY KEY, \
                ingredient_name TEXT UNIQUE NOT NULL)")
    conn.commit()
    cur.execute("CREATE TABLE IF NOT EXISTS measures(measure_id INTEGER PRIMARY KEY, \
                measure_name TEXT UNIQUE)")
    conn.commit()
    cur.execute("CREATE TABLE IF NOT EXISTS recipes(recipe_id INTEGER PRIMARY KEY, \
                recipe_name TEXT NOT NULL, \
                recipe_description TEXT)")
    conn.commit()
    cur.execute("CREATE TABLE IF NOT EXISTS serve(serve_id INTEGER PRIMARY KEY,\
                 recipe_id INTEGER NOT NULL, meal_id INTEGER NOT NULL,\
                 FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id), \
                 FOREIGN KEY(meal_id) REFERENCES meals(meal_id))")
    conn.commit()
    cur.execute("CREATE TABLE IF NOT EXISTS quantity(quantity_id INTEGER PRIMARY KEY, measure_id INTEGER NOT NULL,\
                ingredient_id INTEGER NOT NULL, quantity INTEGER NOT NULL, recipe_id INTEGER NOT NULL, \
                FOREIGN KEY(measure_id) REFERENCES measures(measure_id), \
                FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id), \
                FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id))")
    conn.commit()


def popuni_tabele():
    cur.execute(f"INSERT INTO meals VALUES(1, 'breakfast'), (2, 'brunch'), (3, 'lunch'), (4, 'supper')")
    conn.commit()
    cur.execute("INSERT INTO ingredients VALUES(1, 'milk'), (2, 'cacao'), (3, 'strawberry'), (4, 'blueberry'),\
                (5, 'blackberry'), (6, 'sugar')")
    conn.commit()
    cur.execute("INSERT INTO measures VALUES(1, 'ml'), (2, 'g'), (3, 'l'), (4, 'cup'), \
                (5, 'tbsp'), (6, 'tsp'), (7, 'dsp'), (8, '')")
    conn.commit()


def dodaj_recept(n, o, meals):
    rid = cur.execute(f"INSERT INTO recipes(recipe_name, recipe_description) VALUES('{n}', '{o}')").lastrowid
    conn.commit()
    for m in meals:
        cur.execute(f"INSERT INTO serve(recipe_id, meal_id) VALUES({rid}, {int(m)})")
        conn.commit()
    return rid


def ispisi_sve_obroke():
    cur.execute('SELECT * FROM meals')
    obroci = cur.fetchall()
    ispis = ''
    for o in obroci:
        ispis += f'{o[0]}) {o[1]} '
    print(ispis)


def vrati_mid(n):
    cur.execute(f"SELECT * FROM measures WHERE measure_name LIKE '%{n}%'")
    m = cur.fetchall()
    if m is None or len(m) > 1:
        return None
    return m[0][0]


def vrati_iid(n):
    cur.execute(f"SELECT * FROM ingredients WHERE ingredient_name LIKE '%{n}%'")
    i = cur.fetchall()
    if i is None or len(i) > 1:
        return None
    return i[0][0]


def dodaj_sastojak(s, rid):
    if len(s) == 2:
        m = 8
        i = vrati_iid(s[1])
    else:
        m = vrati_mid(s[1])
        i = vrati_iid(s[2])
    if i is None or m is None:
        print('The ingredient is not conclusive!')
        return
    cur.execute(f"INSERT INTO quantity(measure_id, ingredient_id, quantity, recipe_id) VALUES({m}, {i}, {int(s[0])}, {rid})")
    conn.commit()


def unesi_sastojke(rid):
    while True:
        unos = input('Input quantity of ingredient <press enter to stop>: ')
        if unos == '':
            break
        dodaj_sastojak(unos.split(), rid)


def unosi_recepte():
    while True:
        print('Pass the empty recipe name to exit.')
        naziv = input('Recipe name: ')
        if naziv == '':
            break
        opis = input('Recipe description: ')
        ispisi_sve_obroke()
        meal = input('Enter proposed meals separated by a space: ').split()
        rid = dodaj_recept(naziv, opis, meal)
        unesi_sastojke(rid)


def vrati_id_ing(ing):
    lista = []
    for i in ing:
        cur.execute(f"SELECT ingredient_id FROM ingredients WHERE ingredient_name = '{i}'")
        element = cur.fetchone()
        if element is None:
            return None
        lista.append(element[0])
    return lista


def vrati_id_me(me):
    lista = []
    for m in me:
        cur.execute(f"SELECT meal_id FROM meals WHERE meal_name = '{m}'")
        element = cur.fetchone()
        if element is None:
            return None
        lista.append(element[0])
    return lista


def napravi_string(lista):
    string = '('
    brojac = 0
    for e in lista:
        string += str(e)
        brojac += 1
        if len(lista) != brojac:
            string += ', '
    string += ')'
    return string


def vrati_recepte():
    ing = args.ingredients.split(',')
    me = args.meals.split(',')
    lista_id_ing = vrati_id_ing(ing)
    lista_id_me = vrati_id_me(me)
    if lista_id_ing is None or lista_id_me is None:
        print('There are no such recipes in the database.')
        return
    recepti = 'Recipes selected for you: '
    lm = napravi_string(lista_id_me)
    s1 = set()
    s2 = set()
    s3 = set()
    
    for i in lista_id_ing:
        cur.execute(f"SELECT recipe_name FROM recipes r \
                                JOIN serve s ON r.recipe_id = s.recipe_id \
                                JOIN quantity q ON r.recipe_id = q.recipe_id \
                                WHERE ingredient_id = {i}")
        rez = cur.fetchall()
        if len(s1) == 0:
            for r in rez:
                s1.add(r[0])
        else:
            for r in rez:
                s2.add(r[0])
            s1 = s1.intersection(s2)
        s2 = set()

    for m in lista_id_me:
        cur.execute(f"SELECT recipe_name FROM recipes r \
                                        JOIN serve s ON r.recipe_id = s.recipe_id \
                                        JOIN quantity q ON r.recipe_id = q.recipe_id \
                                        WHERE meal_id IN {lm}")
        rez = cur.fetchall()
        if len(s3) == 0:
            for r in rez:
                s3.add(r[0])
        else:
            for r in rez:
                s2.add(r[0])
            s3 = s3.intersection(s2)
        s2 = set()
    rezultat = s1.intersection(s3)
    for r in rezultat:
        recepti += r
    if r == 'Hot cacao':
        recepti += 'Hot cacao'
    print(recepti)



parser = argparse.ArgumentParser()
parser.add_argument("food_blog")
parser.add_argument("--ingredients")
parser.add_argument("--meals")
args = parser.parse_args()
kreiraj_tabele()
if(args.ingredients is None and args.meals is None):
    popuni_tabele()
    unosi_recepte()
if(args.ingredients is not None and args.meals is not None):
    vrati_recepte()
conn.close()
