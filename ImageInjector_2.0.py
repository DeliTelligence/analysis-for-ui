import psycopg2
import uuid
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta


@dataclass
class StandardWeight:
    standard_weight_id: str
    standard_type: str


@dataclass
class Product:
    product_id: str
    product_name: str
    product_description: str
    product_price: float
    product_type: str
    product_image: bytes
    inventory_id: Optional[str] = None
    standard_weight_products: List['StandardWeightProduct'] = None


@dataclass
class StandardWeightProduct:
    standard_weight_product_id: str
    standard_weight: float
    standard_weight_id: str
    product_id: str


@dataclass
class Inventory:
    inventory_id: str
    total_weight: float
    inventory_value: float
    inventory_expiration_date: datetime
    location: str
    products: List[Product] = None


class DatabaseManager:
    def __init__(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def get_filling_standard_weight(self) -> StandardWeight:
        self.cur.execute("SELECT * FROM TBL_STANDARD_WEIGHT WHERE STANDARD_TYPE = 'FILLING'")
        result = self.cur.fetchone()
        if result:
            return StandardWeight(standard_weight_id=result[0], standard_type=result[1])
        else:
            raise Exception("FILLING standard weight not found in TBL_STANDARD_WEIGHT")

    def get_standard_weight(self, standard_type: str) -> StandardWeight:
        self.cur.execute("SELECT * FROM TBL_STANDARD_WEIGHT WHERE STANDARD_TYPE = %s", (standard_type,))
        result = self.cur.fetchone()
        if result:
            return StandardWeight(standard_weight_id=result[0], standard_type=result[1])
        else:
            raise Exception(f"{standard_type} standard weight not found in TBL_STANDARD_WEIGHT")

    def insert_inventory(self, inventory: Inventory):
        self.cur.execute("""
            INSERT INTO TBL_INVENTORY (INVENTORY_ID, TOTAL_WEIGHT, INVENTORY_VALUE, INVENTORY_EXPIRATION_DATE, LOCATION)
            VALUES (%s, %s, %s, %s, %s)
        """, (inventory.inventory_id, inventory.total_weight, inventory.inventory_value,
              inventory.inventory_expiration_date, inventory.location))

    def insert_product(self, product: Product, standard_weight_product: Optional[StandardWeightProduct] = None,
                       insert_salad: bool = False):
        self.cur.execute("""
            INSERT INTO TBL_PRODUCT (PRODUCT_ID, PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_PRICE, PRODUCT_TYPE, PRODUCT_IMAGE, INVENTORY_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (product.product_id, product.product_name, product.product_description, product.product_price,
              product.product_type, psycopg2.Binary(product.product_image), product.inventory_id))

        if standard_weight_product:
            self.cur.execute("""
                INSERT INTO TBL_STANDARD_WEIGHT_PRODUCT (STANDARD_WEIGHT_PRODUCT_ID, STANDARD_WEIGHT, STANDARD_WEIGHT_ID, PRODUCT_ID)
                VALUES (%s, %s, %s, %s)
            """, (standard_weight_product.standard_weight_product_id, standard_weight_product.standard_weight,
                  standard_weight_product.standard_weight_id, standard_weight_product.product_id))

        if insert_salad:
            salad_standard_weight = self.get_standard_weight("SALAD")
            salad_standard_weight_product_id = str(uuid.uuid4())
            self.cur.execute("""
                INSERT INTO TBL_STANDARD_WEIGHT_PRODUCT (STANDARD_WEIGHT_PRODUCT_ID, STANDARD_WEIGHT, STANDARD_WEIGHT_ID, PRODUCT_ID)
                VALUES (%s, %s, %s, %s)
            """, (salad_standard_weight_product_id,
                  standard_weight_product.standard_weight if standard_weight_product else 0.0,
                  salad_standard_weight.standard_weight_id, product.product_id))


def insert_product_with_inventory(db_manager: DatabaseManager, product_name: str, standard_weight: Optional[float],
                                  product_description: str, product_price: float, product_type: str,
                                  image_path: str, inventory_location: str, inventory_total_weight: float,
                                  inventory_value: float, inventory_expiration_date: datetime,
                                  insert_salad: Optional[float] = None):
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()

        product_id = str(uuid.uuid4())
        inventory_id = str(uuid.uuid4())

        inventory = Inventory(
            inventory_id=inventory_id,
            total_weight=inventory_total_weight,
            inventory_value=inventory_value,
            inventory_expiration_date=inventory_expiration_date,
            location=inventory_location
        )

        product = Product(
            product_id=product_id,
            product_name=product_name,
            product_description=product_description,
            product_price=product_price,
            product_type=product_type,
            product_image=image_data,
            inventory_id=inventory_id
        )

        db_manager.insert_inventory(inventory)
        standard_weight_product = None

        if standard_weight is not None:
            filling_standard_weight = db_manager.get_filling_standard_weight()
            standard_weight_product = StandardWeightProduct(
                standard_weight_product_id=str(uuid.uuid4()),
                standard_weight=standard_weight,
                standard_weight_id=filling_standard_weight.standard_weight_id,
                product_id=product_id
            )

        db_manager.insert_product(product, standard_weight_product)
        if insert_salad is not None:
            salad_standard_weight = db_manager.get_standard_weight("SALAD")
            salad_standard_weight_product_id = str(uuid.uuid4())
            db_manager.cur.execute("""
                INSERT INTO TBL_STANDARD_WEIGHT_PRODUCT (STANDARD_WEIGHT_PRODUCT_ID, STANDARD_WEIGHT, STANDARD_WEIGHT_ID, PRODUCT_ID)
                VALUES (%s, %s, %s, %s)
            """, (salad_standard_weight_product_id,
                  insert_salad,
                  salad_standard_weight.standard_weight_id,
                  product_id))

        db_manager.commit()
        print(f"Product {product_name} with Inventory inserted successfully!")

    except Exception as e:
        print(f"Error inserting product with inventory: {e}")


db_manager = DatabaseManager(dbname="DeliTelligenceDB", user="postgres", password="lemon", host="localhost",
                             port="5432")

try:
    insert_product_with_inventory(
        db_manager,
        product_name='Rasher',
        standard_weight=28.00,
        product_description='Meat of the pig, quite fattening',
        product_price=0.40,
        product_type='BREAKFAST_FOOD',
        image_path=r'C:\Users\I586662\Downloads\RasherFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=1000.0,
        inventory_value=5000.0,
        inventory_expiration_date=datetime.now()
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Hot Egg',
        standard_weight=48.00,
        product_description='Comes from a Chicken, good source of protein',
        product_price=0.60,
        product_type='BREAKFAST_FOOD',
        image_path=r'C:\Users\I586662\Downloads\Egg.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=500.0,
        inventory_value=2000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=90),
        insert_salad=96.00
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Hash Brown',
        standard_weight=56.00,
        product_description='Made from potato in shape of triangle, good source of carbohydrates',
        product_price=0.40,
        product_type='BREAKFAST_FOOD',
        image_path=r'C:\Users\I586662\Downloads\HashBrownFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=750.0,
        inventory_value=2500.0,
        inventory_expiration_date=datetime.now() + timedelta(days=120)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Pudding',
        standard_weight=52.00,
        product_description='Made from pig guts, good source of protein',
        product_price=0.40,
        product_type='BREAKFAST_FOOD',
        image_path=r'C:\Users\I586662\Downloads\PuddingFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=600.0,
        inventory_value=2200.0,
        inventory_expiration_date=datetime.now() + timedelta(days=180)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Sausage',
        standard_weight=80.00,
        product_description='Made from pig guts, good source of protein',
        product_price=0.50,
        product_type='BREAKFAST_FOOD',
        image_path=r'C:\Users\I586662\Downloads\SausageFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=1000.0,
        inventory_value=4000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=150)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Hot Chicken',
        standard_weight=166.00,
        product_description='Comes in different flavours such as spicy, plain and southern fried',
        product_price=2.50,
        product_type='MAIN_FILLING_FOOD',
        image_path=r'C:\Users\I586662\Downloads\HotChickenFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=2000.0,
        inventory_value=8000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=210)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Wedges',
        standard_weight=100.00,
        product_description='Made from potato, good source of carbohydrates',
        product_price=1.00,
        product_type='HOT_FOOD',
        image_path=r'C:\Users\I586662\Downloads\WedgesFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=1500.0,
        inventory_value=3000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=120)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Small Sausage Roll',
        standard_weight=44.00,
        product_description='Sausage wrapped in pastry, good source of protein',
        product_price=0.80,
        product_type='HOT_FOOD',
        image_path=r'C:\Users\I586662\Downloads\SausageRollFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=800.0,
        inventory_value=3200.0,
        inventory_expiration_date=datetime.now() + timedelta(days=90)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Small White Roll',
        standard_weight=78.00,
        product_description='Small roll, good source of carbohydrates',
        product_price=0.90,
        product_type='BREAD',
        image_path=r'C:\Users\I586662\Downloads\SmallRoll.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=600.0,
        inventory_value=2700.0,
        inventory_expiration_date=datetime.now() + timedelta(days=60)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Demi Baguette',
        standard_weight=124.00,
        product_description='Large roll, good source of carbohydrates',
        product_price=1.00,
        product_type='BREAD',
        image_path=r'C:\Users\I586662\Downloads\LargeRoll.jpeg',
        inventory_location='Warehouse A',
        inventory_total_weight=900.0,
        inventory_value=3600.0,
        inventory_expiration_date=datetime.now() + timedelta(days=70)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Jambon',
        standard_weight=108.00,
        product_description='Cheese and Ham wrapped in pastry, good source of carbohydrates',
        product_price=2.00,
        product_type='HOT_FOOD',
        image_path=r'C:\Users\I586662\Downloads\Jambon.webp',
        inventory_location='Warehouse A',
        inventory_total_weight=850.0,
        inventory_value=3400.0,
        inventory_expiration_date=datetime.now() + timedelta(days=100)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Hot Dog Lattice',
        standard_weight=112.00,
        product_description='Mustard and pastry wrapped hot dog, good source of protein',
        product_price=2.50,
        product_type='HOT_FOOD',
        image_path=r'C:\Users\I586662\Downloads\HotDog.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=1100.0,
        inventory_value=4400.0,
        inventory_expiration_date=datetime.now() + timedelta(days=95)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Sliced Bread',
        standard_weight=76.00,
        product_description='Sliced Bread, brow and white, good source of carbohydrates',
        product_price=0.70,
        product_type='BREAD',
        image_path=r'C:\Users\I586662\Downloads\SlicedBread.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=700.0,
        inventory_value=2800.0,
        inventory_expiration_date=datetime.now() + timedelta(days=30)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Wrap',
        standard_weight=64.00,
        product_description='Wrap, brow and white, good source of carbohydrates',
        product_price=0.70,
        product_type='BREAD',
        image_path=r'C:\Users\I586662\Downloads\Wrap.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=1200.0,
        inventory_value=4800.0,
        inventory_expiration_date=datetime.now() + timedelta(days=50)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Rib',
        standard_weight=104.00,
        product_description='Ribs of the pig glazed in Sauce',
        product_price=2.00,
        product_type='HOT_FOOD',
        image_path=r'C:\Users\I586662\Downloads\BurgerAndBBQ.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=1300.0,
        inventory_value=5200.0,
        inventory_expiration_date=datetime.now() + timedelta(days=100)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Burger',
        standard_weight=92.00,
        product_description='Burger meat from the cow, good source of protein',
        product_price=1.70,
        product_type='HOT_FOOD',
        image_path=r'C:\Users\I586662\Downloads\BurgerAndBBQ.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=800.0,
        inventory_value=3200.0,
        inventory_expiration_date=datetime.now() + timedelta(days=85)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Hot Chicken Roll',
        standard_weight=290.00,
        product_description='Staple in the Irish diet, high in protein',
        product_price=3.00,
        product_type='MAIN_FOOD_HOT',
        image_path=r'C:\Users\I586662\Downloads\HotChickenRoll.webp',
        inventory_location='Warehouse A',
        inventory_total_weight=1000.0,
        inventory_value=6000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=140)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Hot Chicken Sandwich',
        standard_weight=242.00,
        product_description='Staple in the Irish diet, high in protein',
        product_price=2.80,
        product_type='MADE_FOOD_HOT',
        image_path=r'C:\Users\I586662\Downloads\HotChickenSandwich.webp',
        inventory_location='Warehouse A',
        inventory_total_weight=950.0,
        inventory_value=5700.0,
        inventory_expiration_date=datetime.now() + timedelta(days=130)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Hot Chicken Wrap',
        standard_weight=230.00,
        product_description='Staple in the Irish diet, high in protein',
        product_price=2.80,
        product_type='MADE_FOOD_HOT',
        image_path=r'C:\Users\I586662\Downloads\HotChickenWrap.webp',
        inventory_location='Warehouse A',
        inventory_total_weight=900.0,
        inventory_value=5000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=120)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Cold Roll',
        standard_weight=124.00,
        product_description='Cold roll, great source of protein and healthy',
        product_price=1.00,
        product_type='MADE_FOOD_COLD',
        image_path=r'C:\Users\I586662\Downloads\ColdRoll.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=700.0,
        inventory_value=2000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=50)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Cold Sandwich',
        standard_weight=76.00,
        product_description='Staple in the Irish diet, high in protein',
        product_price=0.80,
        product_type='MADE_FOOD_COLD',
        image_path=r'C:\Users\I586662\Downloads\ColdSandwich.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=700.0,
        inventory_value=2000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=50)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Cold Wrap',
        standard_weight=64.00,
        product_description='Staple in the Irish diet, Healthier Option',
        product_price=0.70,
        product_type='MADE_FOOD_COLD',
        image_path=r'C:\Users\I586662\Downloads\ColdWrap.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=700.0,
        inventory_value=2000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=50)
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Cold Chicken',
        standard_weight=100.00,
        product_description='High in protein from the chicken',
        product_price=1.00,
        product_type='MAIN_FILLING_FOOD',
        image_path=r'C:\Users\I586662\Downloads\ColdChicken.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=1100.0,
        inventory_expiration_date=datetime.now() + timedelta(days=110),
        inventory_value=5000
    )
    insert_product_with_inventory(
        db_manager,
        product_name='Cajun Chicken',
        standard_weight=100.00,
        product_description='High in protein from the chicken',
        product_price=1.10,
        product_type='MAIN_FILLING_FOOD',
        image_path=r'C:\Users\I586662\Downloads\CajunChicken.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=900.0,
        inventory_value=4500.0,
        inventory_expiration_date=datetime.now() + timedelta(days=110),
        insert_salad=150.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Ham',
        standard_weight=60.00,
        product_description='High in protein from the chicken',
        product_price=0.72,
        product_type='MAIN_FILLING_FOOD',
        image_path=r'C:\Users\I586662\Downloads\HamFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=750.0,
        inventory_value=3000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=130),
        insert_salad=120.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Cheese',
        standard_weight=35.00,
        product_description='High in protein from the cow',
        product_price=0.42,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\CheeseShredded.webp',
        inventory_location='Warehouse A',
        inventory_total_weight=600.0,
        inventory_value=2100.0,
        inventory_expiration_date=datetime.now() + timedelta(days=100),
        insert_salad=70.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Cold Egg',
        standard_weight=48.00,
        product_description='High in protein from the chicken',
        product_price=0.60,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\ColdEggFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=500.0,
        inventory_value=1800.0,
        inventory_expiration_date=datetime.now() + timedelta(days=90),
        insert_salad=96.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Tuna',
        standard_weight=80.00,
        product_description='High in protein from Fish',
        product_price=0.90,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\TunaFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=550.0,
        inventory_value=2700.0,
        inventory_expiration_date=datetime.now() + timedelta(days=150),
        insert_salad=150.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Lettuce',
        standard_weight=15.00,
        product_description='Healthy Rabit food',
        product_price=0.04,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\LettuceFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=700.0,
        inventory_value=1000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=40),
        insert_salad=70.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Onion',
        standard_weight=10.00,
        product_description='Healthy, makes your eyes tear up',
        product_price=0.02,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\OnionFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=300.0,
        inventory_value=500.0,
        inventory_expiration_date=datetime.now() + timedelta(days=30),
        insert_salad=30.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Tomato',
        standard_weight=40.00,
        product_description='High in protein from the cow',
        product_price=0.08,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\TomatoFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=700.0,
        inventory_value=1400.0,
        inventory_expiration_date=datetime.now() + timedelta(days=70),
        insert_salad=70.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Jalapeno',
        standard_weight=15.00,
        product_description='High in protein from the cow',
        product_price=0.12,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\JalapenoFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=300.0,
        inventory_value=600.0,
        inventory_expiration_date=datetime.now() + timedelta(days=60),
        insert_salad=30.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Coleslaw',
        standard_weight=50.00,
        product_description='High in protein from the cow',
        product_price=0.25,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\ColeslawFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=800.0,
        inventory_value=3200.0,
        inventory_expiration_date=datetime.now() + timedelta(days=80),
        insert_salad=80.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Sweetcorn',
        standard_weight=40.00,
        product_description='High in protein from the cow',
        product_price=0.08,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\SweetCornFinal.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=600.0,
        inventory_value=1200.0,
        inventory_expiration_date=datetime.now() + timedelta(days=60),
        insert_salad=60.0
    )

    insert_product_with_inventory(
        db_manager,
        product_name='Salad',
        standard_weight=40.00,
        product_description='Box for a Salad bowl',
        product_price=0.20,
        product_type='COLD_FOOD',
        image_path=r'C:\Users\I586662\Downloads\SaladBox.jpg',
        inventory_location='Warehouse A',
        inventory_total_weight=500.0,
        inventory_value=1000.0,
        inventory_expiration_date=datetime.now() + timedelta(days=50)
    )

finally:
    db_manager.close()