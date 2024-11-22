import psycopg2

def insert_product(product_id, product_name, standard_weight, product_description, product_price, product_type, image_path):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(dbname="DeliTelligenceDB", user="postgres", password="lemon", host="localhost", port="5432")
        cur = conn.cursor()

        # Open image file in binary mode
        with open(image_path, 'rb') as f:
            image_data = f.read()  # Read the image as binary data

        # Insert product details into the database
        cur.execute("""
            INSERT INTO TBL_PRODUCT (
                PRODUCT_ID, PRODUCT_NAME, STANDARD_WEIGHT, 
                PRODUCT_DESCRIPTION, PRODUCT_PRICE, PRODUCT_TYPE, 
                PRODUCT_IMAGE
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            product_id,                   # PRODUCT_ID
            product_name,                 # PRODUCT_NAME
            standard_weight,              # STANDARD_WEIGHT
            product_description,          # PRODUCT_DESCRIPTION
            product_price,                # PRODUCT_PRICE
            product_type,                 # PRODUCT_TYPE
            psycopg2.Binary(image_data)   # PRODUCT_IMAGE (binary data)
        ))

        # Commit the transaction
        conn.commit()

        # Print success message
        print("Product inserted successfully!")

    except Exception as e:
        print(f"Error inserting product: {e}")

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

# Example usage
insert_product(
    product_id='f41578b2-06a0-43c6-959e-abb0a51ea75a7',
    product_name='Rasher',
    standard_weight=28.00,
    product_description='Meat of the pig, quite fattening',
    product_price=0.40,
    product_type='BREAKFAST_FOOD',
    image_path=r'C:\Users\I586662\Downloads\rasher.jpg'
)

insert_product(
    product_id='7d18a54d-1780-42cc-a097-987de0ef382a',
    product_name='Hot Egg',
    standard_weight=48.00,
    product_description='Comes from a Chicken, good source of protein',
    product_price=0.60,
    product_type='BREAKFAST_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Egg.jpg'
)
insert_product(
    product_id='0651ee69-c218-443c-b0e8-7260f84643d9',
    product_name='Hash Brown',
    standard_weight=56.00,
    product_description='Made from potato in shape of triangle, good source of carbohydrates',
    product_price=0.40,
    product_type='BREAKFAST_FOOD',
    image_path=r'C:\Users\I586662\Downloads\HashBrown.jpg'
)
insert_product(
    product_id='0fed4dd6-9ba8-40d1-9f79-9b91c3c9f6cb',
    product_name='Pudding',
    standard_weight=52.00,
    product_description='Made from pig guts, good source of protein',
    product_price=0.40,
    product_type='BREAKFAST_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Pudding.jpg'
)
insert_product(
    product_id='f8828b9e-8561-43d4-9dc9-cdeb3640c696',
    product_name='Hot Chicken',
    standard_weight=166.00,
    product_description='Comes in different flavours such as spicy, plain and southern fried',
    product_price=2.50,
    product_type='MAIN_FILLING_FOOD',
    image_path=r'C:\Users\I586662\Downloads\HotChicken.webp'
)
insert_product(
    product_id='1fac8127-7c95-4876-b1df-ca4d4d0699a2',
    product_name='Wedges',
    standard_weight=100.00,
    product_description='Made from potato, good source of carbohydrates',
    product_price=1.00,
    product_type='HOT_FOOD',
    image_path=r'C:\Users\I586662\Downloads\wedges.jpg'
)
insert_product(
    product_id='83dfa3c8-a844-4701-a0eb-3bbde99ed1f8',
    product_name='Small Sausage Roll',
    standard_weight=44.00,
    product_description='Sausage wrapped in pastry, good source of protein',
    product_price=0.80,
    product_type='HOT_FOOD',
    image_path=r'C:\Users\I586662\Downloads\SausageRoll.jpg'
)
insert_product(
    product_id='86bf0479-1875-43c6-aa6f-9ed726e9a1cb',
    product_name='Small White Roll',
    standard_weight=78.00,
    product_description='Small roll, good source of carbohydrates',
    product_price=0.90,
    product_type='BREAD',
    image_path=r'C:\Users\I586662\Downloads\SmallRoll.jpg'
)
insert_product(
    product_id='eab1a6c1-3191-4dd0-988f-3e10a69441dd',
    product_name='Demi Baguette',
    standard_weight=124.00,
    product_description='Large roll, good source of carbohydrates',
    product_price=1.00,
    product_type='BREAD',
    image_path=r'C:\Users\I586662\Downloads\LargeRoll.jpeg'
)
insert_product(
    product_id='e7a6a858-f28e-401d-8ea5-5bfb1c4d1844',
    product_name='Jambon',
    standard_weight=108.00,
    product_description='Cheese and Ham wrapped in pastry, good source of carbohydrates',
    product_price=2.00,
    product_type='HOT_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Jambon.webp'
)
insert_product(
    product_id='ed905dd9-e05b-42d6-9296-a53e3dd90706',
    product_name='Hot Dog Lattice',
    standard_weight=112.00,
    product_description='Mustard and pastry wrapped hot dog, good source of protein',
    product_price=2.50,
    product_type='HOT_FOOD',
    image_path=r'C:\Users\I586662\Downloads\HotDog.jpg'
)
insert_product(
    product_id='50631d71-4738-4791-91dc-9642c6733ae7',
    product_name='Sliced Bread',
    standard_weight=76.00,
    product_description='Sliced Bread, brow and white, good source of carbohydrates',
    product_price=0.70,
    product_type='BREAD',
    image_path=r'C:\Users\I586662\Downloads\SlicedBread.jpg'
)
insert_product(
    product_id='99503242-d084-4332-9e07-374ecefe045a',
    product_name='Wrap',
    standard_weight=64.00,
    product_description='Wrap, brow and white, good source of carbohydrates',
    product_price=0.70,
    product_type='BREAD',
    image_path=r'C:\Users\I586662\Downloads\Wrap.jpg'
)
insert_product(
    product_id='5e2e1122-b655-4285-9fee-90d3fc777cc4',
    product_name='Rib',
    standard_weight=104.00,
    product_description='Ribs of the pig glazed in Sauce',
    product_price=2.00,
    product_type='HOT_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Ribs.jpg'
)
insert_product(
    product_id='ad26ff15-a208-4a1c-b8eb-e8cc54e66a93',
    product_name='Burger',
    standard_weight=92.00,
    product_description='Burger meat from the cow, good source of protein',
    product_price=1.70,
    product_type='HOT_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Burger.jpg'
)
insert_product(
    product_id='d02ecd53-30d7-45f1-9167-6fe1f84da6b4',
    product_name='Hot Chicken Roll',
    standard_weight=290.00,
    product_description='Staple in the Irish diet, high in protein',
    product_price=3.00,
    product_type='MAIN_FOOD_HOT',
    image_path=r'C:\Users\I586662\Downloads\HotChickenRoll.webp'
)
insert_product(
    product_id='4475909a-671f-409a-a547-300f32856841',
    product_name='Hot Chicken Sandwich',
    standard_weight=242.00,
    product_description='Staple in the Irish diet, high in protein',
    product_price=2.80,
    product_type='MADE_FOOD_HOT',
    image_path=r'C:\Users\I586662\Downloads\HotChickenSandwich.webp'
)

insert_product(
    product_id='8adcfac8-24ea-4705-a44f-4b58d6d5c49c',
    product_name='Hot Chicken Wrap',
    standard_weight=230.00,
    product_description='Staple in the Irish diet, high in protein',
    product_price=2.80,
    product_type='MADE_FOOD_HOT',
    image_path=r'C:\Users\I586662\Downloads\HotChickenWrap.webp'
)

insert_product(
    product_id='d591895a-a838-4f75-8b6f-1bdb3bb77f11',
    product_name='Cold Roll',
    standard_weight=124.00,
    product_description='Cold roll, great source of protein and healthy',
    product_price=1.00,
    product_type='MADE_FOOD_COLD',
    image_path=r'C:\Users\I586662\Downloads\ColdRoll.jpg'
)
insert_product(
    product_id='c64bae03-c122-4bc5-86ca-8ab576fa450a',
    product_name='Cold Sandwich',
    standard_weight=76.00,
    product_description='Staple in the Irish diet, high in protein',
    product_price=0.80,
    product_type='MADE_FOOD_COLD',
    image_path=r'C:\Users\I586662\Downloads\ColdSandwich.jpg'
)
insert_product(
    product_id='cf1d7262-b731-4f51-907b-62a5389fe092',
    product_name='Cold Wrap',
    standard_weight=64.00,
    product_description='Staple in the Irish diet, Healthier Option',
    product_price=0.70,
    product_type='MADE_FOOD_COLD',
    image_path=r'C:\Users\I586662\Downloads\ColdWrap.jpg'
)
insert_product(
    product_id='0af85818-bbc3-4a4d-a726-c4b04e311f73',
    product_name='Cold Chicken',
    standard_weight=100.00,
    product_description='High in protein from the chicken',
    product_price=1.00,
    product_type='MAIN_FILLING_FOOD',
    image_path=r'C:\Users\I586662\Downloads\ColdChicken.jpg'
)
insert_product(
    product_id='a2e89b89-f7c8-4516-a4f4-23b5f431c9d3',
    product_name='Cajun Chicken',
    standard_weight=100.00,
    product_description='High in protein from the chicken',
    product_price=1.10,
    product_type='MAIN_FILLING_FOOD',
    image_path=r'C:\Users\I586662\Downloads\CajunChicken.jpg'
)
insert_product(
    product_id='aa79d640-c316-4354-8edf-dd6d5a0987a1',
    product_name='Ham',
    standard_weight=60.00,
    product_description='High in protein from the chicken',
    product_price=0.72,
    product_type='MAIN_FILLING_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Ham.webp'
)
insert_product(
    product_id='89298482-264c-457d-addd-c22d00de5d19',
    product_name='Cheese',
    standard_weight=35.00,
    product_description='High in protein from the cow',
    product_price=0.42,
    product_type='COLD_FOOD',
    image_path=r'C:\Users\I586662\Downloads\CheeseShredded.webp'
)
insert_product(
    product_id='4a1d0c12-7f14-4b71-8a2d-8eeede90ee30',
    product_name='Cold Egg',
    standard_weight=48.00,
    product_description='High in protein from the chicken',
    product_price=0.60,
    product_type='COLD_FOOD',
    image_path=r'C:\Users\I586662\Downloads\ColdEgg.jpg'
)
insert_product(
    product_id='a72aebeb-f393-4e5f-8569-793ef9a0e3f2',
    product_name='Lettuce',
    standard_weight=15.00,
    product_description='Healthy Rabit food',
    product_price=0.04,
    product_type='COLD_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Lettuce.webp'
)
insert_product(
    product_id='3b771453-2b7a-4185-a6ff-0bc119db23d1',
    product_name='Onion',
    standard_weight=10.00,
    product_description='Healthy, makes your eyes tear up',
    product_price=0.02,
    product_type='COLD_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Onion.webp'
)
insert_product(
    product_id='08721fd3-0592-4f83-8812-e0c0b4aefa3c',
    product_name='Tomato',
    standard_weight=40.00,
    product_description='High in protein from the cow',
    product_price=0.08,
    product_type='COLD_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Tomato.jpg'
)
insert_product(
    product_id='626bbaa6-229b-4d2b-989b-49cdb6e25412',
    product_name='Jalapeno',
    standard_weight=15.00,
    product_description='High in protein from the cow',
    product_price=0.12,
    product_type='COLD_FOOD',
    image_path=r'C:\Users\I586662\Downloads\jalapeno.webp'
)
insert_product(
    product_id='d66dad68-f578-4471-90ce-291d20a0bb7e',
    product_name='Coleslaw',
    standard_weight=50.00,
    product_description='High in protein from the cow',
    product_price=0.25,
    product_type='COLD_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Coleslaw.jpg'
)
insert_product(
    product_id='df49b78b-e2da-40e4-a4bc-19b142023de9',
    product_name='Sweetcorn',
    standard_weight=40.00,
    product_description='High in protein from the cow',
    product_price=0.08,
    product_type='COLD_FOOD',
    image_path=r'C:\Users\I586662\Downloads\Sweetcorn.webp'
)




