import psycopg2
import re
from openpyxl import load_workbook
import json
import os
from pprint import pprint
import xlwt
import uuid


null_type_id = str(uuid.uuid4())
null_service_id = str(uuid.uuid4())
null_type_id_list = []
print("Null type id: " + null_type_id)
print("Null service id: " + null_service_id)

style_cat_id = '3a8e4917-55da-4817-bdcf-1c2a8939b890'
tailor_id = '2023e6e2-dc34-4e6e-a0bf-87bc96b3ee2d'       #(Old service id)
tailor_subcat_id = '29aae573-5250-4c88-8fd7-87b4a230267e'   #use old alterations id for tailor
topfemale_service_id = str(uuid.uuid4())
pantsfemale_service_id = str(uuid.uuid4())

adj_alt_id = '870fb68a-b86b-4687-913d-4d200e659154'     #old adjustments and alterations service id
alteratiions_subcat_id = str(uuid.uuid4())   #Make new alterations subcategory
massage_subcat_id = '4eaf9941-6d29-488c-9653-2f66f2facbb8'

def sqltest(cur):

    myfile = open('categories.csv', 'w', encoding='utf-8')

    #conn = psycopg2.connect("dbname=chozun_15_6_16 user=postgres password=Chozunone")
    #conn = psycopg2.connect("dbname=chozun_test1 user=postgres password=Chozunone")
    ##cur = conn.cursor()

    #cur.execute("""SELECT id from customers_customer""")

    cur.execute("SELECT id, name FROM categories_category;")
    catlist = cur.fetchall()
    #print(catlist)

    for cat in catlist:

        #print(cat[1])
        myfile.write(cat[1] + '\n')

        cur.execute("SELECT category_id, id, name FROM categories_subcategory;")
        subcatlist = cur.fetchall()

        for subcat in subcatlist:

            if subcat[0] == cat[0]:
                #print("\t" + subcat[2])
                myfile.write("\t" + subcat[2] + "\n")

                cur.execute("SELECT sub_category_id, id, name FROM services_service;")
                servicelist = cur.fetchall()

                for service in servicelist:

                    if service[0] == subcat[1]:
                        #print("\t\t" + service[2])
                        myfile.write("\t\t" + service[2] + "\n")


                        cur.execute("SELECT service_id, id, name FROM services_type;")
                        servtypelist = cur.fetchall()

                        for type in servtypelist:

                            if type[0] == service[1]:
                                #print("\t\t\t" + type[2])
                                myfile.write("\t\t\t" + type[2] + "\n")


                                cur.execute("SELECT type_id, id, name FROM services_subtype;")
                                servsubtypelist = cur.fetchall()

                                for subtype in servsubtypelist:

                                    if subtype[0] == type[1]:
                                        #print("\t\t\t\t" + subtype[2])
                                        myfile.write(str("\t\t\t\t" + subtype[2] + "\n"))


    myfile.close()


    cur.execute('SELECT alias4."name" as "category", alias5."name" AS "subcategory", alias1."name" as "service", \
                alias2."name" as "type", alias3."name" as "subtype" FROM "services_type" alias2 \
                JOIN "services_service" alias1 ON  alias1."id" = alias2."service_id" \
                LEFT JOIN "services_subtype" alias3 ON alias2.id = alias3.type_id \
                JOIN "categories_subcategory" alias5 ON alias5.id = alias1.sub_category_id \
                JOIN "categories_category" alias4 on alias4.id = alias5.category_id;')

def styleStruct(cur):

        ####1)Change name of Alterations subcategory to Tailor
    cur.execute("UPDATE ONLY categories_subcategory SET name = 'Tailor' WHERE name = 'Alterations';")

    cur.execute("UPDATE ONLY services_type SET name = 'Trousers' WHERE name = 'Pant';")
    cur.execute("UPDATE ONLY services_type SET name = 'Zip/Button Replacement' WHERE name = 'Zip/ button replacement';")
    cur.execute("UPDATE ONLY services_type SET name = 'Shorten/Lengthen' WHERE name = 'Shorten/ Lengthen';")
    cur.execute("UPDATE ONLY services_type SET name = 'Zip/Velcro/Strap Repair' WHERE name = 'Zip/ velcro/ strap repair';")

    #2)Delete Tailor from services
    cur.execute("DELETE FROM ONLY services_service WHERE name = 'Tailor'")

    #3)Insert all services as previously were stored as types
    # For each element in services_type whos service_id = tailor -> insert into services_service, delete from services_type
    cur.execute("SELECT id, name FROM services_type WHERE service_id = %s::uuid;", (tailor_id,))
    tailorservices = cur.fetchall()


    for service in tailorservices:

        cur.execute("SELECT type_id, name FROM services_subtype WHERE type_id = %s::uuid;", (service[0],))

        #insert new services into services_service and providers_providerservice
        cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, %s, %s::uuid, 0);", (service[0], service[1], tailor_subcat_id,))
        null_type_id = str(uuid.uuid4())
        null_type_id_list.append(null_type_id)
        cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  (null_type_id, service[0],))

        cur.execute("UPDATE ONLY services_type SET name = 'null', placeholder_text = 'null', id = %s::uuid, service_id = %s::uuid  WHERE id = %s::uuid;", (null_type_id, service[0], service[0],))

        cur.execute("UPDATE ONLY services_subtype SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);", (null_type_id, service[0],))


    #Now add men and ladys top/bottom
    #Men
    cur.execute("UPDATE ONLY services_service SET name = 'Top (Male)' WHERE name = 'Top';",)
    cur.execute("UPDATE ONLY services_service SET name = 'Pants (Male)' WHERE name = 'Pant';",)
    #Women
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, 'Top (Female)', %s::uuid, 0);", (topfemale_service_id, tailor_subcat_id,))
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, 'Pants (Female)', %s::uuid, 0);", (pantsfemale_service_id, tailor_subcat_id,))

    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, topfemale_service_id,))

    #one_garment_id = str(uuid.uuid4())  ##Don't think we really need to save id number
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '1 Garment', '1 Garment', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '2 Garment', '2 Garment', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '3+ Garment', '3+ Garment', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))

    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, pantsfemale_service_id,))

    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '1 Garment', '1 Garment', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '2 Garment', '2 Garment', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '3+ Garment', '3+ Garment', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))

    ###Now do same with Alterations
    ###1)Create Alterations subcategory
    cur.execute("INSERT INTO categories_subcategory VALUES (%s::uuid, now(), now(), "
                "'Alterations', 'alterations', '', 0, %s::uuid, False, '#FF79C5E1');", (alteratiions_subcat_id, style_cat_id,))

    #2)Delete Adjustments and Alterations from services
    cur.execute("DELETE FROM ONLY services_service WHERE name = 'Adjustments & alterations'")

    #3)Add previous service types to service list
    cur.execute("SELECT id, name FROM services_type WHERE service_id = %s::uuid;", (adj_alt_id,))
    alterationtypes = cur.fetchall()

    for service in alterationtypes:

        #insert new services into services_service and providers_providerservice
        cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, %s, %s::uuid, 0);", (service[0], service[1], alteratiions_subcat_id,))
        null_type_id = str(uuid.uuid4())
        null_type_id_list.append(null_type_id)
        cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  (null_type_id, service[0],))

        #Change all old type_ids to null ids and their names to 'null' and their service_id to the new services
        cur.execute("UPDATE ONLY services_type SET name = 'null', placeholder_text = 'null', id = %s::uuid, service_id = %s::uuid  WHERE id = %s::uuid;", (null_type_id, service[0], service[0],))

        cur.execute("SELECT name FROM services_subtype WHERE type_id = %s::uuid;", (service[0],))
        subcats = cur.fetchall()

        if len(subcats) != 3:
            cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                        "False, '2 Garment', '2 Garment', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
            cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                        "False, '3+ Garment', '3+ Garment', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))


        #for each subtype have to set old type value to a null value and insert new service value (will be same actual id number)
        #Also have to assig all services with subcatid for new:
        cur.execute("UPDATE ONLY services_subtype SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);", (null_type_id, service[0],))


##Name changes and deletions
    cur.execute("UPDATE ONLY categories_subcategory SET name = 'Shoes' WHERE name = 'Shoe Repair';",)
    cur.execute("UPDATE ONLY services_service SET name = 'Repair' WHERE name = 'Restoration';",)
    cur.execute("DELETE FROM ONLY services_type WHERE id = 'c00e0521-6bae-4cec-9d4d-fb498787f424'") #Delete Restoration-other type
    cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = 'c00e0521-6bae-4cec-9d4d-fb498787f424'") #Delete Restoration-other type

    #Delete style consultation and all associated types
    cur.execute("DELETE FROM ONLY services_service WHERE name = 'Style Consultation'")
    cur.execute("DELETE FROM ONLY services_type WHERE service_id = 'b3ba9f79-ee27-4692-9a65-aadb551c690b'")
    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid;", ('58a3540d-33fa-44cd-b3ff-fd1c2d2d1851', '609e25c5-2bf6-463c-9c25-ab5dc7915eec', 'c13973f3-90bb-462d-801d-e4e0e5c24761', 'c3c2fb41-233d-430e-ade0-26ae4012515b'))


def wellnessStruct(cur):

    wellness_cat_id = '8bcc549a-6d58-4214-987a-06ec365b5904'

    #1)Delete Preggers
    cur.execute("DELETE FROM ONLY services_service WHERE name = 'Pregnancy'")
    cur.execute("DELETE FROM ONLY services_type WHERE service_id = '42e10003-a548-4cb9-8de5-6793454b73f5'")
    cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = '2c96a430-66d5-4856-9f19-fe4bb8329cc2'")
    cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = '443a2886-8b30-474a-9803-794553e6a7f9'")
    cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = 'f559ada4-ae8f-4951-a2f5-1a3d99ec3e74'")
    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = 'f559ada4-ae8f-4951-a2f5-1a3d99ec3e74'")
    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = '443a2886-8b30-474a-9803-794553e6a7f9'")
    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = '2c96a430-66d5-4856-9f19-fe4bb8329cc2'")

    #2)Rename Relaxation -> Classic
    cur.execute("UPDATE ONLY services_service SET name = 'Classic' WHERE name = 'Relaxation';")

    #3) Change reflexology to massage subcat
    reflexology_service_id = 'a1c12a7b-8a66-4a92-ba00-eb0f36cb31ff'
    cur.execute("UPDATE ONLY services_service SET sub_category_id = %s::uuid WHERE id = %s::uuid;", (massage_subcat_id, reflexology_service_id,)) #

    #cur.execute("UPDATE ONLY services_type SET name = 'Back & shoulders' WHERE name = 'Back & Shoulders';")
    #cur.execute("UPDATE ONLY services_type SET name = 'Half body' WHERE name = 'Half Body';")
    #cur.execute("UPDATE ONLY services_type SET name = 'Full body' WHERE name = 'Full Body';")

    cur.execute("UPDATE services_subtype SET name = 'Back & Shoulders' WHERE name = 'Back & shoulders';")
    cur.execute("UPDATE services_subtype SET name = 'Half Body' WHERE name = 'Half body';")
    cur.execute("UPDATE services_subtype SET name = 'Full Body' WHERE name = 'Full body';")

    # #Remove old structure
    # cur.execute("SELECT id FROM services_type WHERE service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid;", ('777cb43b-3994-4fd3-93f4-267c60f6e4c6', '891b65df-2e35-4cdb-a84d-028b9c89c43b', '201cae75-1810-4aa9-bc27-96db7c38fbd1', 'a1c12a7b-8a66-4a92-ba00-eb0f36cb31ff',))
    # type_delete_list = cur.fetchall()
    #
    # for elem in type_delete_list:
    #     cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid;", (elem,))
    #     cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", (elem,))
    #

    def massageRestruct(cur, service_id):

        halfbod_type_id = str(uuid.uuid4())
        fullbod_type_id = str(uuid.uuid4())
        backshoulds_type_id = str(uuid.uuid4())
        foot_type_id = str(uuid.uuid4())

        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Half Body', 'Half Body', %s::uuid, 0, age(now()));", (halfbod_type_id, service_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Full Body', 'Full Body', %s::uuid, 0, age(now()));", (fullbod_type_id, service_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Back & Shoulders', 'Back & Shoulders', %s::uuid, 0, age(now()));", (backshoulds_type_id, service_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Foot', 'Foot', %s::uuid, 0, age(now()));", (foot_type_id, service_id,))

        halfbod_30_subtype_id = str(uuid.uuid4())
        halfbod_60_subtype_id = str(uuid.uuid4())
        halfbod_75_subtype_id = str(uuid.uuid4())
        halfbod_90_subtype_id = str(uuid.uuid4())
        halfbod_120_subtype_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (halfbod_30_subtype_id, halfbod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (halfbod_60_subtype_id, halfbod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '75mins', '75mins', %s::uuid, 0);", (halfbod_75_subtype_id, halfbod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (halfbod_90_subtype_id, halfbod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '120mins', '120mins', %s::uuid, 0);", (halfbod_120_subtype_id, halfbod_type_id,))

        fullbod_30_subtype_id = str(uuid.uuid4())
        fullbod_60_subtype_id = str(uuid.uuid4())
        fullbod_75_subtype_id = str(uuid.uuid4())
        fullbod_90_subtype_id = str(uuid.uuid4())
        fullbod_120_subtype_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (fullbod_30_subtype_id, fullbod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (fullbod_60_subtype_id, fullbod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '75mins', '75mins', %s::uuid, 0);", (fullbod_75_subtype_id, fullbod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (fullbod_90_subtype_id, fullbod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '120mins', '120mins', %s::uuid, 0);", (fullbod_120_subtype_id, fullbod_type_id,))

        backshoulds_30_subtype_id = str(uuid.uuid4())
        backshoulds_60_subtype_id = str(uuid.uuid4())
        backshoulds_75_subtype_id = str(uuid.uuid4())
        backshoulds_90_subtype_id = str(uuid.uuid4())
        backshoulds_120_subtype_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (backshoulds_30_subtype_id, backshoulds_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (backshoulds_60_subtype_id, backshoulds_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '75mins', '75mins', %s::uuid, 0);", (backshoulds_75_subtype_id, backshoulds_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (backshoulds_90_subtype_id, backshoulds_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '120mins', '120mins', %s::uuid, 0);", (backshoulds_120_subtype_id, backshoulds_type_id,))

        foot_30_subtype_id = str(uuid.uuid4())
        foot_60_subtype_id = str(uuid.uuid4())
        foot_75_subtype_id = str(uuid.uuid4())
        foot_90_subtype_id = str(uuid.uuid4())
        foot_120_subtype_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (foot_30_subtype_id, foot_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (foot_60_subtype_id, foot_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '75mins', '75mins', %s::uuid, 0);", (foot_75_subtype_id, foot_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (foot_90_subtype_id, foot_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '120mins', '120mins', %s::uuid, 0);", (foot_120_subtype_id, foot_type_id,))


        cur.execute("SELECT id, name FROM services_type WHERE service_id = %s::uuid;", (service_id,))
        type_id_list = cur.fetchall()

        for elem in type_id_list:
            print(elem[0])
            cur.execute("SELECT id, subtype_id, type_id FROM providers_providerservice WHERE type_id = %s::uuid;", (elem[0],))
            provservlisto = cur.fetchall()
            #provservlist = [item for item in provservlist if item[1] != None]


            for provserv_elem in provservlisto:

                cur.execute("SELECT name FROM services_subtype WHERE id = %s::uuid;", (provserv_elem[1],))
                subtype_name = cur.fetchone()
                subtype_name = str(subtype_name[0])
                cur.execute("SELECT name FROM services_type WHERE id = %s::uuid;", (provserv_elem[2],))
                type_name = cur.fetchone()
                type_name = str(type_name[0])

                #print(str(type_name) + "->" + str(subtype_name))


                if type_name == '75mins' and subtype_name == 'Back & Shoulders':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (backshoulds_75_subtype_id, backshoulds_type_id, provserv_elem[0],)) #

                if type_name == '75mins' and subtype_name == 'Half Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (halfbod_75_subtype_id, halfbod_type_id, provserv_elem[0],)) #

                if type_name == '75mins' and subtype_name == 'Full Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (fullbod_75_subtype_id, fullbod_type_id, provserv_elem[0],)) #

                if type_name == '75mins' and subtype_name == 'Foot':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (foot_75_subtype_id, foot_type_id, provserv_elem[0],)) #


                if type_name == '60mins' and subtype_name == 'Back & Shoulders':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (backshoulds_60_subtype_id, backshoulds_type_id, provserv_elem[0],)) #

                if type_name == '60mins' and subtype_name == 'Half Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (halfbod_60_subtype_id, halfbod_type_id, provserv_elem[0],)) #

                if type_name == '60mins' and subtype_name == 'Full Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (fullbod_60_subtype_id, fullbod_type_id, provserv_elem[0],)) #

                if type_name == '60mins' and subtype_name == 'Foot':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (foot_60_subtype_id, foot_type_id, provserv_elem[0],)) #


                if type_name == '120mins' and subtype_name == 'Back & Shoulders':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (backshoulds_120_subtype_id, backshoulds_type_id, provserv_elem[0],)) #

                if type_name == '120mins' and subtype_name == 'Half Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (halfbod_120_subtype_id, halfbod_type_id, provserv_elem[0],)) #

                if type_name == '120mins' and subtype_name == 'Full Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (fullbod_120_subtype_id, fullbod_type_id, provserv_elem[0],)) #


                if type_name == '30mins' and subtype_name == 'Back & Shoulders':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (backshoulds_30_subtype_id, backshoulds_type_id, provserv_elem[0],)) #

                if type_name == '30mins' and subtype_name == 'Half Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (halfbod_30_subtype_id, halfbod_type_id, provserv_elem[0],)) #

                if type_name == '30mins' and subtype_name == 'Full Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (fullbod_30_subtype_id, fullbod_type_id, provserv_elem[0],)) #

                if type_name == '30mins' and subtype_name == 'Foot':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (foot_30_subtype_id, foot_type_id, provserv_elem[0],)) #

                if type_name == '90mins' and subtype_name == 'Back & Shoulders':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (backshoulds_90_subtype_id, backshoulds_type_id, provserv_elem[0],)) #

                if type_name == '90mins' and subtype_name == 'Half Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (halfbod_90_subtype_id, halfbod_type_id, provserv_elem[0],)) #

                if type_name == '90mins' and subtype_name == 'Full Body':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (fullbod_90_subtype_id, fullbod_type_id, provserv_elem[0],)) #

                if type_name == '90mins' and subtype_name == 'Foot':
                    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE id = %s;", (foot_90_subtype_id, foot_type_id, provserv_elem[0],)) #



        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = %s;", (backshoulds_60_subtype_id, backshoulds_type_id, '229a834b-8191-4a29-89bc-be041a769ab8',)) #


        if service_id == '777cb43b-3994-4fd3-93f4-267c60f6e4c6':

            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = %s::uuid;", (foot_30_subtype_id, foot_type_id, 'c4daee0c-8e0a-405d-b71a-2caabe648e8b',)) #Feet 30mins service
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = %s::uuid;", (foot_60_subtype_id, foot_type_id, '38f036e1-5521-4134-96ea-9f85c977f433')) #Feet 60mins service
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = %s::uuid;", (foot_75_subtype_id, foot_type_id, '31a19d3b-c35e-41d9-8c6e-ad197f04213f')) #Feet 75mins service
        ###Fix foot badboys
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid) AND type_id = (%s::uuid);",  (foot_90_subtype_id, foot_90_subtype_id, 'e9b5a48d-3955-40ec-b0ea-7d8b7b5fec91', 'ccc41ed6-231d-4fc1-b15f-12c7959e1afb',))


    massageRestruct(cur, '777cb43b-3994-4fd3-93f4-267c60f6e4c6')
    massageRestruct(cur, '891b65df-2e35-4cdb-a84d-028b9c89c43b')
    massageRestruct(cur, reflexology_service_id)


    # cur.execute("DELETE FROM ONLY services_service WHERE id = %s::uuid;", ('201cae75-1810-4aa9-bc27-96db7c38fbd1',))


    remedial_30min_type = "f30faac7-fde7-41ca-ad7c-9ba650785c8d"
    remedial_60min_type = "82eaa7b0-3fbc-4b39-84a2-491f0da92ae6"
    remedial_75min_type = "2abdaef0-e1ad-4b2e-a80b-9b704b6f550c"
    remedial_90min_type = "be7ff0c3-cd03-49c0-96ee-42a48da7ce0f"
    remedial_120min_type = "6dda45f6-7009-4eab-9ad9-f0f406e53b7e"
    min75_type_id = '0cda07f6-8a42-4062-aa6c-2a4ffe94c9a2'      #New Back and Shoulders id
    min60_type_id = '4faeba6b-8625-48c6-98b6-7b7364e01eda'      #New Half Body id
    min120_type_id = '9386a6b2-fb89-45ac-bbbe-fe6a6082e43d'     #New Full body id
    min30_type_id = 'd5a007ef-febc-4a4d-a23b-f66498227ecf'      #New Foot id
    min90_type_id = 'e9b5a48d-3955-40ec-b0ea-7d8b7b5fec91'

    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", (min30_type_id, min60_type_id, min75_type_id, min90_type_id, min120_type_id))
    cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid;", (min30_type_id, min60_type_id, min75_type_id, min90_type_id, min120_type_id))

    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", (remedial_30min_type, remedial_60min_type, remedial_75min_type, remedial_90min_type, remedial_120min_type))
    cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid;", (remedial_30min_type, remedial_60min_type, remedial_75min_type, remedial_90min_type, remedial_120min_type))

    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", ('31a19d3b-c35e-41d9-8c6e-ad197f04213f', '38f036e1-5521-4134-96ea-9f85c977f433', 'c4daee0c-8e0a-405d-b71a-2caabe648e8b'))
    cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid;", ('31a19d3b-c35e-41d9-8c6e-ad197f04213f', '38f036e1-5521-4134-96ea-9f85c977f433', 'c4daee0c-8e0a-405d-b71a-2caabe648e8b'))

    cur.execute("DELETE FROM ONLY services_service WHERE id = %s::uuid;", ('201cae75-1810-4aa9-bc27-96db7c38fbd1',))



#Create new type for all massage types
    def newType(cur, name, subcat_id):

        new_service_id = str(uuid.uuid4())

        back_shoulds_type_id = str(uuid.uuid4())
        half_bod_type_id = str(uuid.uuid4())
        full_bod_type_id = str(uuid.uuid4())
        foot_type_id = str(uuid.uuid4())

        cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                    "False, %s, %s::uuid, 0);", (new_service_id, name, subcat_id,))

        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Back & shoulders', 'Back & shoulders', %s::uuid, 0, age(now()));", (back_shoulds_type_id, new_service_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Half body', 'Half body', %s::uuid, 0, age(now()));", (half_bod_type_id, new_service_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Full body', 'Full body', %s::uuid, 0, age(now()));", (full_bod_type_id, new_service_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Feet', 'Feet', %s::uuid, 0, age(now()));", (foot_type_id, new_service_id,))


        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), back_shoulds_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), back_shoulds_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '75mins', '75mins', %s::uuid, 0);", (str(uuid.uuid4()), back_shoulds_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (str(uuid.uuid4()), back_shoulds_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '120mins', '120mins', %s::uuid, 0);", (str(uuid.uuid4()), back_shoulds_type_id,))

        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), half_bod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), half_bod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '75mins', '75mins', %s::uuid, 0);", (str(uuid.uuid4()), half_bod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (str(uuid.uuid4()), half_bod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '120mins', '120mins', %s::uuid, 0);", (str(uuid.uuid4()), half_bod_type_id,))

        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '75mins', '75mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '120mins', '120mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))

        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), foot_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), foot_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '75mins', '75mins', %s::uuid, 0);", (str(uuid.uuid4()), foot_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (str(uuid.uuid4()), foot_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '120mins', '120mins', %s::uuid, 0);", (str(uuid.uuid4()), foot_type_id,))

    newType(cur, "Thai", massage_subcat_id)
    newType(cur, "Aromatherapy", massage_subcat_id)
    #newType(cur, "Hot Stone", massage_subcat_id)

    new_service_id = str(uuid.uuid4())

    back_shoulds_type_id = str(uuid.uuid4())
    half_bod_type_id = str(uuid.uuid4())
    full_bod_type_id = str(uuid.uuid4())
    foot_type_id = str(uuid.uuid4())

    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, 'Hot Stone', %s::uuid, 0);", (new_service_id, massage_subcat_id,))

    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Full body', 'Full body', %s::uuid, 0, age(now()));", (full_bod_type_id, new_service_id,))

    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '75mins', '75mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '90mins', '90mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '120mins', '120mins', %s::uuid, 0);", (str(uuid.uuid4()), full_bod_type_id,))

####Body Subcategory
    body_subcat_id = '48dd263c-0060-4530-908b-01bb79c65182'
    cur.execute("UPDATE ONLY categories_subcategory SET name = 'Body' WHERE id = %s::uuid;", (body_subcat_id,))

    physio_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                    "False, 'Physio', %s::uuid, 0);", (physio_service_id, body_subcat_id,))

    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, physio_service_id,))

    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))

    newType(cur, "Acupuncture", body_subcat_id)

    ##Cupping - add subtypes to types and update provserv
    cup_wet_type_id = '1ce9251d-369a-4b3a-aa31-2000cf6154f7'
    cup_dry_type_id = '74efb560-4565-4edd-aaf6-26a5c35d2337'
    cup_massage_type_id = '75399435-e7b7-4f87-8320-76da8d30263e'

    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '20mins', '20mins', %s::uuid, 0);", (str(uuid.uuid4()), cup_wet_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), cup_wet_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), cup_wet_type_id,))

    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '20mins', '20mins', %s::uuid, 0);", (str(uuid.uuid4()), cup_dry_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), cup_dry_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), cup_dry_type_id,))

    cup_mass_20mins_id = str(uuid.uuid4())
    cup_mass_30mins_id = str(uuid.uuid4())
    cup_mass_60mins_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '20mins', '20mins', %s::uuid, 0);", (cup_mass_20mins_id, cup_massage_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (cup_mass_30mins_id, cup_massage_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (cup_mass_60mins_id, cup_massage_type_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid WHERE id = 11608;", (cup_mass_20mins_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid WHERE id = 12978;", (cup_mass_60mins_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid WHERE id = 12281;", (cup_mass_20mins_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid WHERE id = 11653;", (cup_mass_20mins_id,))

    footbath_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                    "False, 'Foot Bath', %s::uuid, 0);", (footbath_service_id, body_subcat_id,))
    old_footbath_type_id = 'b80e7b73-4d18-4450-8a3e-6bace3913cd6'
    cur.execute("UPDATE ONLY services_type SET service_id = %s::uuid, name = 'null' WHERE id = %s::uuid;", (footbath_service_id, old_footbath_type_id,))

    bodyscrub_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                    "False, 'Body Scrub', %s::uuid, 0);", (bodyscrub_service_id, body_subcat_id,))
    old_bodyscrub_type_id = 'c6a011e9-6e30-490a-812e-fbc168e4b597'
    cur.execute("UPDATE ONLY services_type SET service_id = %s::uuid, name = 'null' WHERE id = %s::uuid;", (bodyscrub_service_id, old_bodyscrub_type_id,))

    bodywrap_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                    "False, 'Body Wrap', %s::uuid, 0);", (bodywrap_service_id, body_subcat_id,))
    old_bodywrap_type_id = 'c8004de4-d4e2-4e49-870f-244b42872c7c'
    cur.execute("UPDATE ONLY services_type SET service_id = %s::uuid, name = 'null' WHERE id = %s::uuid;", (bodywrap_service_id, old_bodywrap_type_id,))

    null_type_id_list.append(old_bodywrap_type_id)
    null_type_id_list.append(old_bodyscrub_type_id)
    null_type_id_list.append(old_footbath_type_id)


    ###Add 30mins to above subtypes
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), old_footbath_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), old_bodyscrub_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), old_bodywrap_type_id,))

    cur.execute("DELETE FROM ONLY services_service WHERE id = 'cf2b1c4e-9b87-454d-95fa-af0a7b9eafe2'")


#####Mind subcategory
    mind_subcat_id = 'c6f193e6-a754-430d-b852-efa696884e1e'
    cur.execute("UPDATE ONLY categories_subcategory SET name = 'Mind' WHERE id = %s::uuid;", (mind_subcat_id,))

    meditate_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                    "False, 'Meditation', %s::uuid, 0);", (meditate_service_id, mind_subcat_id,))


    zen_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Zen', 'Zen', %s::uuid, 0, age(now()));", (zen_type_id, meditate_service_id,))

    mindfulness_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Meditate', 'Meditate', %s::uuid, 0, age(now()));", (mindfulness_type_id, meditate_service_id,))

    sound_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Sound', 'Sound', %s::uuid, 0, age(now()));", (sound_type_id, meditate_service_id,))


    zen_60min_subtype_id = str(uuid.uuid4())
    zen_90min_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (zen_60min_subtype_id, zen_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (zen_90min_subtype_id, zen_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), zen_type_id,))

    mindful_60min_subtype_id = str(uuid.uuid4())
    mindful_90min_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (mindful_60min_subtype_id, mindfulness_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (mindful_90min_subtype_id, mindfulness_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), mindfulness_type_id,))

    sound_60min_subtype_id = str(uuid.uuid4())
    sound_90min_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (sound_60min_subtype_id, sound_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (sound_90min_subtype_id, sound_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), sound_type_id,))

#Now rename all ids in provserv to fit these
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (zen_type_id, zen_60min_subtype_id, '20d243c5-5b33-459a-86cc-3d1b4b3236f0', '492138e7-0679-4b84-ab3f-191c0fac4f92', '6a3ec6a6-0e9d-4d59-877a-01a15f9e40fd'))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (zen_type_id, zen_90min_subtype_id, '058af349-8426-467a-9977-804289f4d225', '1a56a149-cd3d-463b-99be-272173dec7fe', 'bcae7954-38e4-4363-b48c-e3702af3d9c6'))

    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (mindfulness_type_id, mindful_60min_subtype_id, '4ead2d96-02c4-429b-9f51-b77926b20ac6', '7f1c2986-c227-4a10-915d-84949b60ed5f', 'cd13cc84-663f-4f95-a7b1-70fec3c3f98b'))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (mindfulness_type_id, mindful_90min_subtype_id, 'f2a82c8f-70d5-4935-977d-d2e7095bf175', 'ae15ede2-86d1-4a4c-adfc-f0799a2b3777', '6ce19d14-1abc-4e7c-af2a-636f869a602e'))

    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (sound_type_id, sound_60min_subtype_id, '11d54e28-50c1-4ff9-aea7-8cefec25eebe', '6832bb96-0ad5-4c78-9410-bcf07f2ff33f', 'a0f171b8-a979-4047-9bd3-3faa27dbf19e'))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (sound_type_id, sound_90min_subtype_id, '9ecc44f5-8f7f-46b8-b861-cdfea249716a', '289ad28a-fb05-4a99-a3e6-1bd03aada9f4', '2446c06f-f6e3-4363-bfa8-dd07100f1644'))


    flotation_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                    "False, 'Floatation', %s::uuid, 0);", (flotation_service_id, mind_subcat_id,))
    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, flotation_service_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))

    #Delete old types/subtypes
    #Float spa
    cur.execute("DELETE FROM ONLY services_type WHERE id = 'ca0ed1d8-fee1-4c13-bc9e-3ceabfe751da';")
    cur.execute("DELETE FROM ONLY services_service WHERE id = '078156e2-1de8-40ee-bc4a-e263902c2503';")
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (sound_type_id, sound_90min_subtype_id, '9ecc44f5-8f7f-46b8-b861-cdfea249716a', '289ad28a-fb05-4a99-a3e6-1bd03aada9f4', '2446c06f-f6e3-4363-bfa8-dd07100f1644'))

    #Zen/mindfulness/sound
    cur.execute("DELETE FROM ONLY services_service WHERE id = '05da0f1e-766e-4628-913d-d3e3cab8bb1c';")
    cur.execute("DELETE FROM ONLY services_service WHERE id = '66ffd98b-de2b-40c4-8858-9c8338c1b9b8';")
    cur.execute("DELETE FROM ONLY services_service WHERE id = '14f4673c-2283-4bb4-a679-38fea66be1a9';")

    cur.execute("DELETE FROM ONLY services_type WHERE service_id = '05da0f1e-766e-4628-913d-d3e3cab8bb1c';")
    cur.execute("DELETE FROM ONLY services_type WHERE service_id = '66ffd98b-de2b-40c4-8858-9c8338c1b9b8';")
    cur.execute("DELETE FROM ONLY services_type WHERE service_id = '14f4673c-2283-4bb4-a679-38fea66be1a9';")

    cur.execute("DELETE FROM ONLY services_subtype WHERE name = 'No reason';")
    cur.execute("DELETE FROM ONLY services_subtype WHERE name = 'Stress';")
    cur.execute("DELETE FROM ONLY services_subtype WHERE name = 'Medical';")


    ###Movement
    movement_subcat_id = str(uuid.uuid4())
    cur.execute("INSERT INTO categories_subcategory VALUES (%s::uuid, now(), now(), "
                "'Movement', 'Movement', '', 0, %s::uuid, False, '#FFB18DC0');", (movement_subcat_id, wellness_cat_id,))

    pilates_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                    "False, 'Pilates', %s::uuid, 0);", (pilates_service_id, movement_subcat_id,))
    yoga_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                    "False, 'Yoga', %s::uuid, 0);", (yoga_service_id, movement_subcat_id,))


    pilat_ind_type_id = str(uuid.uuid4())
    pilat_ind_60_subtype_id = str(uuid.uuid4())
    pilat_ind_90_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Individual', 'Individual', %s::uuid, 0, age(now()));", (pilat_ind_type_id, pilates_service_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), pilat_ind_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (pilat_ind_60_subtype_id, pilat_ind_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (pilat_ind_90_subtype_id, pilat_ind_type_id,))

    pilat_group_type_id = str(uuid.uuid4())
    pilat_group_60_subtype_id = str(uuid.uuid4())
    pilat_group_90_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Group', 'Group', %s::uuid, 0, age(now()));", (pilat_group_type_id, pilates_service_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), pilat_group_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (pilat_group_60_subtype_id, pilat_group_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (pilat_group_90_subtype_id, pilat_group_type_id,))


    yoga_ind_type_id = str(uuid.uuid4())
    yoga_ind_60_subtype_id = str(uuid.uuid4())
    yoga_ind_90_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Individual', 'Individual', %s::uuid, 0, age(now()));", (yoga_ind_type_id, yoga_service_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), yoga_ind_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (yoga_ind_60_subtype_id, yoga_ind_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (yoga_ind_90_subtype_id, yoga_ind_type_id,))

    yoga_group_type_id = str(uuid.uuid4())
    yoga_group_60_subtype_id = str(uuid.uuid4())
    yoga_group_90_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Group', 'Group', %s::uuid, 0, age(now()));", (yoga_group_type_id, yoga_service_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), yoga_group_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '60mins', '60mins', %s::uuid, 0);", (yoga_group_60_subtype_id, yoga_group_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '90mins', '90mins', %s::uuid, 0);", (yoga_group_90_subtype_id, yoga_group_type_id,))


    ##Change ids of movement entries in provserv
    #individual 60mins pilates
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (pilat_ind_type_id, pilat_ind_60_subtype_id, 'e49b6724-3d19-402f-9d53-e6285bbb34c8', 'a4d32973-2f15-4a8a-a683-382d3680f26a', '9dc4a583-67a1-4874-b3ee-c0f0506aa61d',))
    #group 60mins pilates
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (pilat_group_type_id, pilat_group_60_subtype_id, '72c47518-5acd-4a0f-98af-f748c5a036db', '8595b2db-f821-4e12-a2d6-fe29942bb3a7', 'f9d2e182-8acf-40e0-a850-f0cb64460342',))

    #individual 90mins pilates
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (pilat_ind_type_id, pilat_ind_90_subtype_id, '32bcf527-f1c6-442a-8db9-16a88f1d4337', '6ac35e08-8576-409f-93fd-144638e598ce', 'ed8f3507-a436-4fcb-b1bb-af126fcc23ad',))
    #group 90mins pilates
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (pilat_group_type_id, pilat_group_90_subtype_id, 'c5ebabe3-b35d-4815-b004-c7430fe11f54', '282eaf10-daba-4a4b-9eee-107bf33206f2', '495659eb-b1c5-4b92-89af-dfcd39517f10',))


    #individual 60mins yoga
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (yoga_ind_type_id, yoga_ind_60_subtype_id, 'bffcebb6-3708-4648-abd9-4c1faafb163a', '45a5f6ff-734c-4689-8902-7e4382749ad6', '1c1106ae-fb57-4e50-9d93-37e551a9f9a5',))
    #group 60mins yoga
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (yoga_group_type_id, yoga_group_60_subtype_id, 'b286bd59-14e5-411d-bfe6-52b0f1ead820', '088085a5-3d54-4ca2-b68f-9badb40af9e5', 'c8297a23-8eb6-4f40-ba24-7e57f40e399b',))

    #individual 90mins yoga
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (yoga_ind_type_id, yoga_ind_90_subtype_id, 'a45d8c12-7e8b-437e-954b-6f093a1161ea', 'c4eec14b-8d06-4bb5-a14c-e071d561a8ec', '865171e9-4d34-45f8-bd7f-1edea00eb05e',))
    #group 90mins yoga
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = %s::uuid OR subtype_id = %s::uuid OR subtype_id = %s::uuid;", (yoga_group_type_id, yoga_group_90_subtype_id, 'b0df0709-a54c-4d5e-bed7-2e5b677dda13', '1443ec28-baed-4c85-99b8-4945c026e75a', 'bf452d4d-bdc6-4229-b846-22c4a93a203b',))


    #Delete old structure
    cur.execute("DELETE FROM ONLY categories_subcategory WHERE name = 'Pilates';")
    cur.execute("DELETE FROM ONLY categories_subcategory WHERE name = 'Yoga';")

    cur.execute("DELETE FROM ONLY services_service WHERE sub_category_id = 'f58d2ff4-f117-4ad6-ac9d-ec48c61a8826';")
    cur.execute("DELETE FROM ONLY services_service WHERE sub_category_id = 'd15e5887-dcb9-4b89-9a00-34663833a1b2';")

    #pilates
    cur.execute("SELECT id FROM services_type WHERE service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid ;", ('14e6d227-aa9f-459c-8781-3edd3f4c7066', '8ecfedc1-eb77-4f10-b139-792321b33356', 'c50689cc-bab1-46dd-b0f0-4f9ab255da79',))
    pilatlist = cur.fetchall()

    for elem in pilatlist:
        cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", (elem))
        cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid;", (elem))

    #yoga
    cur.execute("SELECT id FROM services_type WHERE service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid ;", ('65698188-71a2-489a-aca9-3bca4a788e57', 'a750fa7f-baf1-4f50-b6ea-56086e8d7d93', 'e8c00928-43d1-4fc0-834c-2f9d0698f089',))
    yogalist = cur.fetchall()

    for elem in yogalist:
        cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", (elem))
        cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid;", (elem))


def groomingStruct(cur):

    cur.execute("UPDATE ONLY categories_subcategory SET name = 'Hair (Female)' WHERE id = %s::uuid;", ('360c2dab-0859-4db5-a9c5-8fe5ad6a0c0f',))
    cur.execute("UPDATE ONLY services_service SET name = 'Special Occasion' WHERE name = 'Occasional Hair';")

    #Add toner type
    def colourstructure(cur, type_name, colour_service_id):

        type_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, %s, %s, %s::uuid, 0, age(now()));", (type_id, type_name, type_name, colour_service_id,))

        junior_subtype_id = str(uuid.uuid4())
        standard_subtype_id = str(uuid.uuid4())
        senior_subtype_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, 'Junior Stylist', 'Junior Stylist', %s::uuid, 0);", (junior_subtype_id, type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, 'Standard Stylist', 'Standard Stylist', %s::uuid, 0);", (standard_subtype_id, type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, 'Senior Stylist', 'Senior Stylist', %s::uuid, 0);", (senior_subtype_id, type_id,))

        return type_id, junior_subtype_id, standard_subtype_id, senior_subtype_id


    colour_service_id = "fb4d01af-3bc6-487a-924b-7c01b73b4b25"

    balayage_type_id, junior_balayage_subcat_id, standard_balayage_subcat_id, senior_balayage_subcat_id = colourstructure(cur, "Balayage", colour_service_id)
    ombre_type_id, junior_ombre_subcat_id, standard_ombre_subcat_id, senior_ombre_subcat_id = colourstructure(cur, "Ombre", colour_service_id)
    semi_type_id, junior_semi_subcat_id, standard_semi_subcat_id, senior_semi_subcat_id = colourstructure(cur, "Semi", colour_service_id)
    toner_type_id, junior_toner_subcat_id, standard_toner_subcat_id, senior_toner_subcat_id = colourstructure(cur, "Toner", colour_service_id)
    halfhead_type_id, junior_halfhead_subcat_id, standard_halfhead_subcat_id, senior_halfhead_subcat_id = colourstructure(cur, "Half Head Foils", colour_service_id)
    fullhead_type_id, junior_fullhead_subcat_id, standard_fullhead_subcat_id, senior_fullhead_subcat_id = colourstructure(cur, "Full Head Foils", colour_service_id)
    partline_type_id, junior_partline_subcat_id, standard_partline_subcat_id, senior_partline_subcat_id = colourstructure(cur, "Part Line Foils", colour_service_id)
    quarterhead_type_id, junior_quarterhead_subcat_id, standard_quarterhead_subcat_id, senior_quarterhead_subcat_id = colourstructure(cur, "Quarter Head Foils", colour_service_id)
    regrowth_type_id, junior_regrowth_subcat_id, standard_regrowth_subcat_id, senior_regrowth_subcat_id = colourstructure(cur, "Regrowth", colour_service_id)
    colourcorrect_type_id, junior_colourcorrect_subcat_id, standard_colourcorrect_subcat_id, senior_colourcorrect_subcat_id = colourstructure(cur, "Colour Correction", colour_service_id)
    tint_type_id, junior_tint_subcat_id, standard_tint_subcat_id, senior_tint_subcat_id = colourstructure(cur, "Tint", colour_service_id)



    #Toner
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE type_id = (%s::uuid);",  (junior_toner_subcat_id, toner_type_id, 'd54ff528-b1f2-43d5-ab82-6afe1091ef46',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE type_id = (%s::uuid);",  (standard_toner_subcat_id, toner_type_id, '9e35b5d9-fece-4f47-a5bb-58d8595fa4a1',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE type_id = (%s::uuid);",  (senior_toner_subcat_id, toner_type_id, '3f9be0ab-ac5e-4c74-8c35-6c1bcc1db417',))

    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", ('d54ff528-b1f2-43d5-ab82-6afe1091ef46',))
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", ('9e35b5d9-fece-4f47-a5bb-58d8595fa4a1',))
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", ('3f9be0ab-ac5e-4c74-8c35-6c1bcc1db417',))
    cur.execute("DELETE FROM ONLY services_service WHERE id = %s::uuid;", ('039e5afe-23d6-4f79-ae2d-c7d97c077d35',))    #Toner

    cur.execute("DELETE FROM ONLY services_service WHERE id = %s::uuid;", ('46c23efe-e359-4cf4-ac24-721b4c930bb9',))    #Shave

    #Balayage
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE type_id = (%s::uuid);",  (standard_balayage_subcat_id, balayage_type_id, 'ba584a49-4a02-4365-9863-46e44ca3cac0',))

    #Ombre
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE type_id = (%s::uuid);",  (standard_ombre_subcat_id, ombre_type_id, '11dfc809-5410-44a3-8b83-2bc9fbc01d50',))

    #Baliage subtype
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid) OR subtype_id = (%s::uuid);",  (standard_balayage_subcat_id, balayage_type_id, '60907b7a-b188-4af5-92ba-d03a16dae343', '97068d55-228f-46aa-a1f4-47c550ec63f0',))
    #Full head subtype
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid) OR subtype_id = (%s::uuid);",  (standard_fullhead_subcat_id, fullhead_type_id, 'fc4db139-49cd-4dab-b7e0-27f9963dc0cb', '480b13e4-587d-454e-8539-c3e4a426d2c0',))
    #Half head subtype
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid) OR subtype_id = (%s::uuid) OR subtype_id = (%s::uuid);",  (standard_halfhead_subcat_id, halfhead_type_id, '82ac94ba-02c0-4c83-bc6f-b09ac4e3b552', '169f539e-6602-4e7c-968c-63ca1f48ae10', '3b123b60-398c-4de9-b0b1-ac6a2852dce0',))
    #Foils subtype - put in semi perm?
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid) OR subtype_id = (%s::uuid);",  (standard_semi_subcat_id, semi_type_id, 'f424b733-5732-4134-8010-30e29be1df39', '75c75d8d-d69d-4a34-942d-f25a0ceec734',))
    #Part line foils
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (standard_partline_subcat_id, partline_type_id, 'cb48de88-7c1f-41f2-9717-5f8e889d010a',))
    #1/4 head
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (standard_quarterhead_subcat_id, quarterhead_type_id, 'c56b2ea1-e94d-4b99-9432-db2dc18c0a72',))
    #Highlights -> regrowth
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (standard_regrowth_subcat_id, regrowth_type_id, '55535dba-8434-4c20-9d58-d1e35896e233',))


    typo_delete_list = ['ba584a49-4a02-4365-9863-46e44ca3cac0', '11dfc809-5410-44a3-8b83-2bc9fbc01d50', '907c438e-6b0b-4ec1-b87f-1c677d89424a', '9c07a9c5-05a3-4fb5-bc74-c5411df8ea50', 'bcbf0535-87d7-4b0d-b238-7299ad870c06']
    for typo in typo_delete_list:
        cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", (typo,))
        cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid;", (typo,))

    #Change names of all length subtypes to stylists
    cur.execute("UPDATE ONLY services_type SET name = 'Junior Stylist' WHERE name = 'Short Length';")
    cur.execute("UPDATE ONLY services_type SET name = 'Standard Stylist' WHERE name = 'Medium Length';")
    cur.execute("UPDATE ONLY services_type SET name = 'Senior Stylist' WHERE name = 'Long Length';")

    fringetrim_type_id = '24d7efa9-1739-4852-9504-5844812cebe7'
    junior_frintrim_subcat_id = str(uuid.uuid4())
    standard_frintrim_subcat_id = str(uuid.uuid4())
    senior_frintrim_subcat_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Junior Stylist', 'Junior Stylist', %s::uuid, 0);", (junior_frintrim_subcat_id, fringetrim_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Standard Stylist', 'Standard Stylist', %s::uuid, 0);", (standard_frintrim_subcat_id, fringetrim_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Senior Stylist', 'Senior Stylist', %s::uuid, 0);", (senior_frintrim_subcat_id, fringetrim_type_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE type_id = (%s::uuid);",  (standard_frintrim_subcat_id, fringetrim_type_id,))


    def treatmentstructure(cur, type_name, treatment_service_id):

        type_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, %s, %s, %s::uuid, 0, age(now()));", (type_id, type_name, type_name, treatment_service_id,))

        short_subcat_id = str(uuid.uuid4())
        med_subcat_id = str(uuid.uuid4())
        long_subcat_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, 'Short Length', 'Short Length', %s::uuid, 0);", (short_subcat_id, type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, 'Medium Length', 'Medium Length', %s::uuid, 0);", (med_subcat_id, type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, 'Long Length', 'Long Length', %s::uuid, 0);", (long_subcat_id, type_id,))

        return type_id, short_subcat_id, med_subcat_id, long_subcat_id

    old_short_dry_subcat_id = 'dd98750a-03d0-4b08-9e3c-4c3d65035596'
    old_short_oily_subcat_id = 'b1471021-0901-403f-9d54-3b814283c3f6'
    old_short_thin_subcat_id = '7a42788d-7283-4d2d-884b-76632c62a037'
    old_short_thick_subcat_id = '848f2eb2-9a16-4d67-9fb5-2f62efc6c937'

    old_med_dry_subcat_id = '96474d71-86c0-4ecf-a26f-fda65ae7f18f'
    old_med_oily_subcat_id = 'f37c5047-6b46-4f12-b99b-f384e1d929e5'
    old_med_thin_subcat_id = '29d43261-d60e-468b-8a48-006f5400e7b0'
    old_med_thick_subcat_id = '4dc03e21-b1ec-48f4-a57a-4e1acf7af6f7'

    old_long_dry_subcat_id = '84e2b299-dc9f-4992-992c-139bdf50ef51'
    old_long_oily_subcat_id = '25ba474b-eccc-4371-a049-dbd4c1a27d80'
    old_long_thin_subcat_id = '0b4f153f-04f4-4406-b94d-28a8d0a904cf'
    old_long_thick_subcat_id = '17b82264-b8c0-42c8-bb8a-308cd2a1ad5e'

    old_med_type_id = '6ece444d-b398-4108-9e88-6c6ecb09d160'

    treatment_service_id = 'bc9e857f-07b2-4bdd-aafe-8861b3afbbb1'

    thin_type_id, short_thin_subcat_id, med_thin_subcat_id, long_thin_subcat_id = treatmentstructure(cur, "Thin", treatment_service_id)
    thick_type_id, short_thick_subcat_id, med_thick_subcat_id, long_thick_subcat_id = treatmentstructure(cur, "Thick", treatment_service_id)
    oily_type_id, short_oily_subcat_id, med_oily_subcat_id, long_oily_subcat_id = treatmentstructure(cur, "Oily", treatment_service_id)
    dry_type_id, short_dry_subcat_id, med_dry_subcat_id, long_dry_subcat_id = treatmentstructure(cur, "Dry", treatment_service_id)


    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (short_thin_subcat_id, thin_type_id, old_short_thin_subcat_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (med_thin_subcat_id, thin_type_id, old_med_thin_subcat_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (long_thin_subcat_id, thin_type_id, old_long_thin_subcat_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (short_thick_subcat_id, thick_type_id, old_short_thick_subcat_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (med_thick_subcat_id, thick_type_id, old_med_thick_subcat_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (long_thick_subcat_id, thick_type_id, old_long_thick_subcat_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (short_oily_subcat_id, oily_type_id, old_short_oily_subcat_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (med_oily_subcat_id, oily_type_id, old_med_oily_subcat_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (long_oily_subcat_id, oily_type_id, old_long_oily_subcat_id,))


    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (short_dry_subcat_id, dry_type_id, old_short_dry_subcat_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (med_dry_subcat_id, dry_type_id, old_med_dry_subcat_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (long_dry_subcat_id, dry_type_id, old_long_dry_subcat_id,))
    #Now change entries with empty subtype
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE type_id = (%s::uuid);",  (med_dry_subcat_id, dry_type_id, old_med_type_id,))

    ##Delete old oily structure
    cur.execute("DELETE FROM ONLY services_subtype WHERE name = 'Oily' OR name = 'Dry' OR name = 'Thick' OR name = 'Thin';")
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", ('4f00398f-23fd-4e3d-acb2-7fb53a2f6dc7', '6dd5b4d2-26c4-4fa0-a3ce-bc96e764bfa2', '6ece444d-b398-4108-9e88-6c6ecb09d160'))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE id = %s OR id = %s;",  (short_thin_subcat_id, thin_type_id, '13704', '13736',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE id = %s OR id = %s;",  (long_thin_subcat_id, thin_type_id, '13703', '13944',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE id = %s OR id = %s;",  (med_thin_subcat_id, thin_type_id, '13693', '13705',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE id = %s OR id = %s;",  (med_thin_subcat_id, thin_type_id, '13737', '13784',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE id = %s OR id = %s;",  (med_thin_subcat_id, thin_type_id, '13960', '14079',))

    cur.execute("SELECT id FROM providers_providerservice ")
    provserv_list = cur.fetchall()
    max_id = max(provserv_list)[0]

    cur.execute("SELECT * FROM providers_providerservice WHERE subtype_id =%s::uuid;", (short_thin_subcat_id,))
    thin_type_list = cur.fetchall()

    for elem in thin_type_list:
        max_id = max_id + 1
        cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], short_thick_subcat_id, thick_type_id, elem[5],))
        max_id = max_id + 1
        cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], short_dry_subcat_id, dry_type_id, elem[5],))
        max_id = max_id + 1
        cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], short_oily_subcat_id, oily_type_id, elem[5],))
#Med
    cur.execute("SELECT * FROM providers_providerservice WHERE subtype_id = %s::uuid;", (med_thin_subcat_id,))
    thin_type_list = cur.fetchall()
    for elem in thin_type_list:
        max_id = max_id + 1
        cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], med_thick_subcat_id, thick_type_id, elem[5],))
        max_id = max_id + 1
        cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], med_dry_subcat_id, dry_type_id, elem[5],))
        max_id = max_id + 1
        cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], med_oily_subcat_id, oily_type_id, elem[5],))
#Long
    cur.execute("SELECT * FROM providers_providerservice WHERE subtype_id = %s::uuid;", (long_thin_subcat_id,))
    thin_type_list = cur.fetchall()
    for elem in thin_type_list:
        max_id = max_id + 1
        cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], long_thick_subcat_id, thick_type_id, elem[5],))
        max_id = max_id + 1
        cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], long_dry_subcat_id, dry_type_id, elem[5],))
        max_id = max_id + 1
        cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], long_oily_subcat_id, oily_type_id, elem[5],))



    ##For inserting null type into permanent straightening, use treatment structure function
    perm_straight_service_id = 'c18f2184-c018-4647-958f-e90c507ef1de'
    null_type_id, short_permstraight_subcat_id, med_permstraight_subcat_id, long_permstraight_subcat_id = treatmentstructure(cur, "null", perm_straight_service_id)
    null_type_id_list.append(null_type_id)
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE type_id = (%s::uuid);",  (short_permstraight_subcat_id, null_type_id, '116b710e-a37d-499b-9d1a-77463d3c6958',))#Short Length
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE type_id = (%s::uuid);",  (med_permstraight_subcat_id, null_type_id, '98319b8f-5287-41f7-a6a4-9bc0b3277637',))#Med Length
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE type_id = (%s::uuid);",  (long_permstraight_subcat_id, null_type_id, '73637357-4e72-4ce0-9de6-f5cdd5d52704',))#Long Length

    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", ('116b710e-a37d-499b-9d1a-77463d3c6958', '73637357-4e72-4ce0-9de6-f5cdd5d52704', '98319b8f-5287-41f7-a6a4-9bc0b3277637'))

#Hair (Male)
    male_hair_subcat_id = str(uuid.uuid4())
    cur.execute("INSERT INTO categories_subcategory VALUES (%s::uuid, now(), now(), "
                "'Hair (Male)', 'Hair (Male)', '', 0, %s::uuid, False, '#FF79C5E1');", (male_hair_subcat_id, '97e0fbb7-85a8-4e4e-bb67-2700cf7347d1',))

    hair_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
            "False, 'Hair', %s::uuid, 0);", (hair_service_id, male_hair_subcat_id,))

    buzzcut_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Buzzcut', 'Buzzcut', %s::uuid, 0, age(now()));", (buzzcut_type_id, hair_service_id,))
    backsides_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Back and Sides', 'Back and Sides', %s::uuid, 0, age(now()));", (backsides_type_id, hair_service_id,))
    trim_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Trim', 'Trim', %s::uuid, 0, age(now()));", (trim_type_id, hair_service_id,))
    style_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Style', 'Style', %s::uuid, 0, age(now()));", (style_type_id, hair_service_id,))
    washcut_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Wash and Cut', 'Wash and Cut', %s::uuid, 0, age(now()));", (washcut_type_id, hair_service_id,))

    beard_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
            "False, 'Beard', %s::uuid, 0);", (beard_service_id, male_hair_subcat_id,))

    straightrazor_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Straight Razor', 'Straight Razor', %s::uuid, 0, age(now()));", (straightrazor_type_id, beard_service_id,))
    beardtrim_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Beard Trim', 'Beard Trim', %s::uuid, 0, age(now()));", (beardtrim_type_id, beard_service_id,))
    stdshave_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Standard Shave', 'Standard Shave', %s::uuid, 0, age(now()));", (stdshave_type_id, beard_service_id,))


    hair_beard_service_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
            "False, 'Hair and Beard', %s::uuid, 0);", (hair_beard_service_id, male_hair_subcat_id,))

    std_hairbeard_type_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Standard', 'Standard', %s::uuid, 0, age(now()));", (std_hairbeard_type_id, hair_beard_service_id,))

    #Update provserv
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid WHERE type_id = (%s::uuid);",  (stdshave_type_id, 'a2fb4ce3-c97b-4737-8e34-2413b32e2b15',))#Standard Shave
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE type_id = (%s::uuid);",  (beardtrim_type_id, None, '18ebbb1a-832c-4a3e-b640-fc9ce04e6ab4',))#Beard trim
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid WHERE type_id = (%s::uuid);",  (straightrazor_type_id, '9a42a3d4-0ad6-40e2-8c72-de33ccad1b4f',))#Straight razor

    #Change subtype names to stylists
    cur.execute("UPDATE ONLY services_subtype SET name = 'Junior Stylist' WHERE name = 'Short Length' AND type_id = (%s::uuid);",  ('0181ccd2-792d-40f5-866b-623f844df2e4',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Junior Stylist' WHERE name = 'Short Length' AND type_id = (%s::uuid);",  ('14feaa0f-09d0-47d8-a389-77505e919200',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Junior Stylist' WHERE name = 'Short Length' AND type_id = (%s::uuid);",  ('e020fedd-2c8f-40c3-9922-4398c8647fa2',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Junior Stylist' WHERE name = 'Short Length' AND type_id = (%s::uuid);",  ('56a1b756-fb26-4680-9913-ebdcc48b1573',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Junior Stylist' WHERE name = 'Short Length' AND type_id = (%s::uuid);",  ('a94a119a-4136-4ea9-8abf-e69f2ae93b7b',))

    cur.execute("UPDATE ONLY services_subtype SET name = 'Standard Stylist' WHERE name = 'Medium Length' AND type_id = (%s::uuid);",  ('0181ccd2-792d-40f5-866b-623f844df2e4',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Standard Stylist' WHERE name = 'Medium Length' AND type_id = (%s::uuid);",  ('14feaa0f-09d0-47d8-a389-77505e919200',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Standard Stylist' WHERE name = 'Medium Length' AND type_id = (%s::uuid);",  ('e020fedd-2c8f-40c3-9922-4398c8647fa2',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Standard Stylist' WHERE name = 'Medium Length' AND type_id = (%s::uuid);",  ('56a1b756-fb26-4680-9913-ebdcc48b1573',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Standard Stylist' WHERE name = 'Medium Length' AND type_id = (%s::uuid);",  ('a94a119a-4136-4ea9-8abf-e69f2ae93b7b',))

    cur.execute("UPDATE ONLY services_subtype SET name = 'Senior Stylist' WHERE name = 'Long Length' AND type_id = (%s::uuid);",  ('0181ccd2-792d-40f5-866b-623f844df2e4',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Senior Stylist' WHERE name = 'Long Length' AND type_id = (%s::uuid);",  ('14feaa0f-09d0-47d8-a389-77505e919200',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Senior Stylist' WHERE name = 'Long Length' AND type_id = (%s::uuid);",  ('e020fedd-2c8f-40c3-9922-4398c8647fa2',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Senior Stylist' WHERE name = 'Long Length' AND type_id = (%s::uuid);",  ('56a1b756-fb26-4680-9913-ebdcc48b1573',))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Senior Stylist' WHERE name = 'Long Length' AND type_id = (%s::uuid);",  ('a94a119a-4136-4ea9-8abf-e69f2ae93b7b',))

    cur.execute("UPDATE ONLY services_type SET name = 'Standard Cut' WHERE id = (%s::uuid);",  ('a94a119a-4136-4ea9-8abf-e69f2ae93b7b',))


    #Delete old beard types/subtypes
    cur.execute("SELECT id FROM services_type WHERE service_id = %s::uuid;", ('46c23efe-e359-4cf4-ac24-721b4c930bb9',))
    oldbeardlist = cur.fetchall()

    for elem in oldbeardlist:
        cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", (elem))
        cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid;", (elem))

    #Make up - add null type
    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, 'a47b4500-d565-4050-8ff7-8370bf983f38',))
    makeover90_subtype_id = str(uuid.uuid4())
    makeover60_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '90mins', '90mins', %s::uuid, 0);", (makeover90_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '60mins', '60mins', %s::uuid, 0);", (makeover60_subtype_id, null_type_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (makeover90_subtype_id, null_type_id, '69ede853-d886-4e45-8562-4ecb477fbb9a',))#90min makeober
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (makeover60_subtype_id, null_type_id, 'ef649856-a3d9-42ea-a316-a3cee84fb757',))#60min makeober


    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, 'c24aa216-0808-43b8-93f5-6b4b33c51e42',))
    occasion_30_subtype_id = str(uuid.uuid4())
    occasion_60_subtype_id = str(uuid.uuid4())

    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '30mins', '30mins', %s::uuid, 0);", (occasion_30_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '60mins', '60mins', %s::uuid, 0);", (occasion_60_subtype_id, null_type_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (occasion_30_subtype_id, null_type_id, '56f36e33-9b28-40c9-849c-c641347998a8',))#90min makeober
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (occasion_60_subtype_id, null_type_id, 'f852dbab-000c-4bf7-a1a1-cb700196c6ae',))#60min makeober


    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, 'f58cad33-d554-43dc-b117-cfe1dc74adf7',))
    professional_30_subtype_id = str(uuid.uuid4())
    professional_60_subtype_id = str(uuid.uuid4())

    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '30mins', '30mins', %s::uuid, 0);", (professional_30_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '60mins', '60mins', %s::uuid, 0);", (professional_60_subtype_id, null_type_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (professional_30_subtype_id, null_type_id, 'c111705f-1434-4596-90df-ebcc2ccd3f57',))#30min makeober
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (professional_60_subtype_id, null_type_id, 'b0508495-538a-465d-9542-105deeb35d9f',))#60min makeober

    #Delete all old type structures
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid;", ('c111705f-1434-4596-90df-ebcc2ccd3f57', 'b0508495-538a-465d-9542-105deeb35d9f',))
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid;", ('56f36e33-9b28-40c9-849c-c641347998a8', 'f852dbab-000c-4bf7-a1a1-cb700196c6ae',))
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid;", ('69ede853-d886-4e45-8562-4ecb477fbb9a', 'ef649856-a3d9-42ea-a316-a3cee84fb757',))


    #Nails
    #File and paint
    old_standard_type_id = '2bef66ac-f229-422a-a72c-e30bafd8845f'
    old_shellac_type_id = 'cc3bffbb-deb1-4763-95c9-af17ef4b4a45'
    #Standard->Feet
    cur.execute("UPDATE ONLY services_type SET name = 'Feet' WHERE id = (%s::uuid);",  (old_standard_type_id,))
    #Shellac->Hands
    cur.execute("UPDATE ONLY services_type SET name = 'Hands' WHERE id = (%s::uuid);",  (old_shellac_type_id,))

    old_feet_standard_subtype_id = '661b0b93-0a1d-4534-ba89-ad150094a182'
    old_hands_standard_subtype_id = '7e9cdb8c-798e-45b4-aa62-e324b48c27da'
    old_feet_shellac_subtype_id = '43417ef3-68c2-4fc7-9da2-8d417b250534'
    old_hands_shellac_subtype_id = '2fe1e1e8-f9ea-4fd1-a098-d61213b815b0'

    cur.execute("UPDATE ONLY services_subtype SET name = 'Standard Polish' WHERE id = (%s::uuid);",  (old_feet_standard_subtype_id, ))
    cur.execute("UPDATE ONLY services_subtype SET name = 'Shellac' WHERE id = (%s::uuid);",  (old_hands_standard_subtype_id, )) #Feet->shellac no holds hands->standard

    cur.execute("UPDATE ONLY services_subtype SET name = 'Standard Polish' WHERE id = (%s::uuid);",  (old_feet_shellac_subtype_id, ))#Hands->standard now holds
    cur.execute("UPDATE ONLY services_subtype SET name = 'Shellac' WHERE id = (%s::uuid);",  (old_hands_shellac_subtype_id, )) #Feet->shellac no holds hands->standard


    #Provserv
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (old_shellac_type_id, old_feet_shellac_subtype_id, old_hands_standard_subtype_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = %s::uuid, subtype_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (old_standard_type_id, old_hands_standard_subtype_id, old_feet_shellac_subtype_id,))


    #Insert null type into manicure
    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, '71c1049a-db3a-4f6f-9304-bb34d7380c73',))
    express_subtype_id = str(uuid.uuid4())
    standardpolish_subtype_id = str(uuid.uuid4())
    shellac_subtype_id = str(uuid.uuid4())

    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Express', 'Express', %s::uuid, 0);", (express_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Standard Polish', 'Standard Polish', %s::uuid, 0);", (standardpolish_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Shellac', 'Shellac', %s::uuid, 0);", (shellac_subtype_id, null_type_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (express_subtype_id, null_type_id, '2345c9d4-041e-4b41-8327-b9975bfc01d4',))#30min makeober
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (standardpolish_subtype_id, null_type_id, '3a515f76-16e5-4377-898f-32115a93a0ab',))#60min makeober
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (shellac_subtype_id, null_type_id, '699b081b-afd7-47d2-b35e-1a7f49874ddb',))#60min makeober

    #Delete all old type structures
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", ('2345c9d4-041e-4b41-8327-b9975bfc01d4', '3a515f76-16e5-4377-898f-32115a93a0ab', '699b081b-afd7-47d2-b35e-1a7f49874ddb',))

    #Mani and Pedi
    #Insert null type
    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, 'f2cfdbe6-d2f5-4340-ac29-27dc82a4e41d',))
    express_mp_subtype_id = str(uuid.uuid4())
    standard_mp_subtype_id = str(uuid.uuid4())
    shellac_mp_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Express', 'Express', %s::uuid, 0);", (express_mp_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Standard', 'Standard', %s::uuid, 0);", (standard_mp_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Shellac', 'Shellac', %s::uuid, 0);", (shellac_mp_subtype_id, null_type_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (express_mp_subtype_id, null_type_id, 'c73239ef-60e9-4844-9aae-c89191ee0883',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (standard_mp_subtype_id, null_type_id, '10414c84-f637-4b0b-b1ea-b7d6bfc455c2',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (shellac_mp_subtype_id, null_type_id, '00be87e4-9357-460c-9365-589e8563ebd4',))

    #Delete all old type structures
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", ('c73239ef-60e9-4844-9aae-c89191ee0883', '10414c84-f637-4b0b-b1ea-b7d6bfc455c2', '00be87e4-9357-460c-9365-589e8563ebd4',))

    #Pedicure
    #Insert null type
    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, 'f6f9709a-5997-437c-afae-9c0607afda6e',))
    express_mp_subtype_id = str(uuid.uuid4())
    standard_mp_subtype_id = str(uuid.uuid4())
    shellac_mp_subtype_id = str(uuid.uuid4())
    spa_mp_subtype_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Express', 'Express', %s::uuid, 0);", (express_mp_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Standard', 'Standard', %s::uuid, 0);", (standard_mp_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Shellac', 'Shellac', %s::uuid, 0);", (shellac_mp_subtype_id, null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'Spa', 'Spa', %s::uuid, 0);", (spa_mp_subtype_id, null_type_id,))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (express_mp_subtype_id, null_type_id, '0ad3c827-ace3-4fbe-b820-ea34e9724762',))

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (standard_mp_subtype_id, null_type_id, 'ec6bc85b-959a-447d-8dbf-6a2161bda992',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (shellac_mp_subtype_id, null_type_id, 'aabb9832-9eea-4bf8-b66b-f31d4b788a91',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = (%s::uuid) OR subtype_id = (%s::uuid);",  (spa_mp_subtype_id, null_type_id, '3e4f2831-58c1-4a95-97dc-72194a4214a7', '0f537b30-8afd-420a-adb7-0a8d04eebca5',))

    #Delete all old type structures
    cur.execute("DELETE FROM ONLY services_subtype WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", ('ec6bc85b-959a-447d-8dbf-6a2161bda992', 'aabb9832-9eea-4bf8-b66b-f31d4b788a91', '3e4f2831-58c1-4a95-97dc-72194a4214a7', '0f537b30-8afd-420a-adb7-0a8d04eebca5',))
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", ('0ad3c827-ace3-4fbe-b820-ea34e9724762', '006c9559-58b7-4466-92b1-cccc562b6178', '1c68dd6b-6942-4002-b98f-5a244a2350c0',))

    #Laser
    cur.execute("SELECT id FROM services_subtype WHERE name = 'Sensitive Skin' OR name = 'Normal Skin';")
    laser_subcat_list = cur.fetchall()

    for elem in laser_subcat_list:

        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (None, elem[0],))
        cur.execute("DELETE FROM ONLY services_subtype WHERE id = %s::uuid;", (elem[0],))

    #Facial
    cur.execute("SELECT id FROM services_subtype WHERE name = 'Sensitive skin' OR name = 'Oily skin' OR name = 'Dry skin';")
    facial_subcat_list = cur.fetchall()

    for elem in facial_subcat_list:

        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid WHERE subtype_id = (%s::uuid);",  (None, elem[0],))
        cur.execute("DELETE FROM ONLY services_subtype WHERE id = %s::uuid;", (elem[0],))


    #Eyebrow Art
    eyebrow_subcat_id = str(uuid.uuid4())
    cur.execute("INSERT INTO categories_subcategory VALUES (%s::uuid, now(), now(), "
                "'Eyebrow', 'Eyebrow', '', 0, %s::uuid, False, '#FF79C5E1');", (eyebrow_subcat_id, '97e0fbb7-85a8-4e4e-bb67-2700cf7347d1',))

    cur.execute("UPDATE ONLY services_service SET name = 'Art', sub_category_id = %s::uuid WHERE name = 'Eyebrow Art';",  (eyebrow_subcat_id,))
    cur.execute("UPDATE ONLY services_service SET sub_category_id = %s::uuid WHERE name = 'Tint';",  (eyebrow_subcat_id,))

###Fixing fuckup - insert fuckedupdata into junior/std/snr stylists
    ###To be executed after preprocessing of errors so may still look like an error
    #Short Length
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = %s::uuid AND type_id = %s::uuid;",  (junior_semi_subcat_id, semi_type_id, 'd1da1d43-f82e-419e-b1f3-fff1cbfa4595', '907c438e-6b0b-4ec1-b87f-1c677d89424a',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = %s::uuid AND type_id = %s::uuid;",  (junior_semi_subcat_id, semi_type_id, '971568a2-88a0-4a4a-ba6f-78c351712d69', '907c438e-6b0b-4ec1-b87f-1c677d89424a',))
    #Medium Length
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = %s::uuid AND type_id = %s::uuid;",  (standard_semi_subcat_id, semi_type_id, 'e8a55b9a-cd31-481a-9a8a-71b54eed26de', '907c438e-6b0b-4ec1-b87f-1c677d89424a',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = %s::uuid AND type_id = %s::uuid;",  (standard_semi_subcat_id, semi_type_id, '9236dffe-2064-4b54-be25-af227cebadfc', '907c438e-6b0b-4ec1-b87f-1c677d89424a',))
    #Long Length
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = %s::uuid AND type_id = %s::uuid;",  (senior_semi_subcat_id, semi_type_id, '224c0944-97eb-4160-873b-bb6a4f00ada7', '907c438e-6b0b-4ec1-b87f-1c677d89424a',))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE subtype_id = %s::uuid AND type_id = %s::uuid;",  (senior_semi_subcat_id, semi_type_id, '61cf863c-53e8-49b2-80f0-4ec2ae17161a', '907c438e-6b0b-4ec1-b87f-1c677d89424a',))



def localStruct(cur):


    def insertGroupInd(cur, service_id, hrs_2_type_id, hrs_4_type_id, hrs_8_type_id):

        #Insert group/ind into type
        ind_type_id = str(uuid.uuid4())
        group_type_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Individual', 'Individual', %s::uuid, 0, age(now()));", (ind_type_id, service_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                    "False, 'Group', 'Group', %s::uuid, 0, age(now()));", (group_type_id, service_id,))

        ind_2hrs_subtype_id = str(uuid.uuid4())
        ind_4hrs_subtype_id = str(uuid.uuid4())
        ind_8hrs_subtype_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '2 hours', '2 hours', %s::uuid, 0);", (ind_2hrs_subtype_id, ind_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '4 hours', '4 hours', %s::uuid, 0);", (ind_4hrs_subtype_id, ind_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '8 hours', '8 hours', %s::uuid, 0);", (ind_8hrs_subtype_id, ind_type_id,))

        group_2hrs_subtype_id = str(uuid.uuid4())
        group_4hrs_subtype_id = str(uuid.uuid4())
        group_8hrs_subtype_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '2 hours', '2 hours', %s::uuid, 0);", (group_2hrs_subtype_id, group_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '4 hours', '4 hours', %s::uuid, 0);", (group_4hrs_subtype_id, group_type_id,))
        cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                    "False, '8 hours', '8 hours', %s::uuid, 0);", (group_8hrs_subtype_id, group_type_id,))

        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (group_2hrs_subtype_id, group_type_id, hrs_2_type_id))
        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (group_4hrs_subtype_id, group_type_id, hrs_4_type_id))
        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (group_8hrs_subtype_id, group_type_id, hrs_8_type_id))

        cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", (hrs_2_type_id, hrs_4_type_id, hrs_8_type_id,))

        return group_type_id, group_2hrs_subtype_id, group_4hrs_subtype_id, group_8hrs_subtype_id

    cg_2hrs_type_id = '0487fd9c-61d0-4389-aedf-b79a4a40d62c'
    cg_4hrs_type_id = '3fe7034b-ecdf-4a78-985a-48003721b8ba'
    cg_8hrs_type_id = 'f9c167ec-a9bf-42cf-90bd-312a9f1e1b52'
    sight_2hrs_type_id = '7f22e996-b912-488d-b852-f62d957dff9b'
    sight_4hrs_type_id = '4805c0ea-6f58-4c14-b8b7-5c9ebe87fb55'
    sight_8hrs_type_id = 'ddb78c75-d28c-4164-b030-02571908dc97'

    #type/subtype ids needed for changing tailored to me pricelist
    cg_group_type_id, cg_group_2hrs_subtype_id, cg_group_4hrs_subtype_id, cg_group_8hrs_subtype_id = insertGroupInd(cur, '0283675d-6d15-49b5-a95a-255ac190971b', cg_2hrs_type_id, cg_4hrs_type_id, cg_8hrs_type_id,) #City guide
    sight_group_type_id, sight_group_2hrs_subtype_id, sight_group_4hrs_subtype_id, sight_group_8hrs_subtype_id = insertGroupInd(cur, '344ce75a-b48c-4e66-817a-7c3a43a8a482', sight_2hrs_type_id, sight_4hrs_type_id, sight_8hrs_type_id,) #Sightseeing
    insertGroupInd(cur, '84282718-94c1-4044-b166-6ed7a01fbc03', 'cc923606-db3a-4d5d-b7ed-12403503d967', 'd1c5d8c2-82e2-4b5f-975c-a6b8de2f3b27', '24a738ee-1b09-40ce-908b-d2198aac049a',) #Countryside

    tailored_me_2hrs_type_id = 'fb8d7fc1-1c4b-493c-b746-a0ec30e338e3'
    tailored_me_4hrs_type_id = '79ab212f-738e-4928-8f38-395df3b830f1'
    tailored_me_8hrs_type_id = '05676253-f9e3-428e-9b65-82839cc60df0'

    cur.execute("SELECT * FROM providers_providerservice WHERE type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid;", (tailored_me_2hrs_type_id, tailored_me_4hrs_type_id, tailored_me_8hrs_type_id,))
    tailored_me_list = cur.fetchall()

    #For elements in tailored to me, duplicate and put in both sightseeing and city guide
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (cg_group_2hrs_subtype_id, cg_group_type_id, tailored_me_2hrs_type_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (cg_group_4hrs_subtype_id, cg_group_type_id, tailored_me_4hrs_type_id,))
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (cg_group_8hrs_subtype_id, cg_group_type_id, tailored_me_8hrs_type_id,))

    cur.execute("SELECT id FROM providers_providerservice ")
    provserv_list = cur.fetchall()
    max_id = max(provserv_list)[0]

    for elem in tailored_me_list:

        max_id = max_id + 1

        ###Have to insert into prov serv with sightseeing groupp type/subtype ids
        if elem[4] == tailored_me_2hrs_type_id:   #2 hours
            cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], sight_group_2hrs_subtype_id, sight_group_type_id, elem[5],))

        if elem[4] == tailored_me_4hrs_type_id:   #4 hours
            cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], sight_group_4hrs_subtype_id, sight_group_type_id, elem[5],))

        if elem[4] == tailored_me_8hrs_type_id:   #4 hours
            cur.execute("INSERT INTO providers_providerservice VALUES (%s, %s, %s::uuid, %s::uuid, %s::uuid, %s);", (max_id, elem[1], elem[2], sight_group_8hrs_subtype_id, sight_group_type_id, elem[5],))

        #Now delete tailored to me type
        cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", (tailored_me_2hrs_type_id, tailored_me_4hrs_type_id, tailored_me_8hrs_type_id,))
        cur.execute("DELETE FROM ONLY services_service WHERE name = 'Tailored to me';")

    #Translation
    def translationInsert(cur, language):

        langserv_subcat_id = '71d1fb44-7cdb-4624-8497-202b9d6534ac'

        lang_serv_id = str(uuid.uuid4())
        cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, %s, %s::uuid, 0);", (lang_serv_id, language, langserv_subcat_id,))

        english_type_id = str(uuid.uuid4())
        french_type_id = str(uuid.uuid4())
        spanish_type_id = str(uuid.uuid4())
        italian_type_id = str(uuid.uuid4())

        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'English', 'English', %s::uuid, 0, age(now()));", (english_type_id, lang_serv_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'French', 'French', %s::uuid, 0, age(now()));", (french_type_id, lang_serv_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Spanish', 'Spanish', %s::uuid, 0, age(now()));", (spanish_type_id, lang_serv_id,))
        cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'Italian', 'Italian', %s::uuid, 0, age(now()));", (italian_type_id, lang_serv_id,))

        langlist = [english_type_id, french_type_id, spanish_type_id, italian_type_id]

        for lang_type_id in langlist:

            hrs_1_subtype_id = str(uuid.uuid4())
            hrs_2_subtype_id = str(uuid.uuid4())
            hrs_4_subtype_id = str(uuid.uuid4())
            hrs_6_subtype_id = str(uuid.uuid4())
            hrs_8_subtype_id = str(uuid.uuid4())
            cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                        "False, '1 hour', '1 hour', %s::uuid, 0);", (hrs_1_subtype_id, lang_type_id,))
            cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                        "False, '2 hours', '2 hours', %s::uuid, 0);", (hrs_2_subtype_id, lang_type_id,))
            cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                        "False, '4 hours', '4 hours', %s::uuid, 0);", (hrs_4_subtype_id, lang_type_id,))
            cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                        "False, '6 hours', '6 hours', %s::uuid, 0);", (hrs_6_subtype_id, lang_type_id,))
            cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                        "False, '8 hours', '8 hours', %s::uuid, 0);", (hrs_8_subtype_id, lang_type_id,))

            if lang_type_id == english_type_id:
                subtype_return_list = [hrs_1_subtype_id, hrs_2_subtype_id, hrs_4_subtype_id, hrs_6_subtype_id, hrs_8_subtype_id]

        return english_type_id, subtype_return_list

    translationInsert(cur, "Cantonese Translation")
    translationInsert(cur, "Thai Translation")
    translationInsert(cur, "Malaysian Translation")
    english_type_id, english_subtype_list = translationInsert(cur, "Mandarin Translation")

    old_eng_type_list = ['614208bf-cda1-4077-ae92-7dfd289bff36', 'bbacc7ab-88b3-45bc-9fa8-c761fd76f715', '76effc9e-8452-423d-8f85-07db5f8459dc', '98b626f3-b1b3-49f9-96ff-330316c0c09d', '68d12335-bf6d-4a0d-953e-942a8cda2903']
    old_span_type_list = ['d11b6849-612c-4c35-896a-d225bbaced0a', '39fdedde-3885-451d-b006-591c3ba36802', '566d9ff9-fd1a-471e-bf67-f4eff5f2d380', '68e5ab29-eaef-41c7-8fb7-1b25f4bc627f', '982b0a47-fd32-4e66-b05b-81bc4200c07e']


    i=0

    for elem in old_eng_type_list:

        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = (%s::uuid);",  (english_subtype_list[i], english_type_id, elem,))
        i=i+1

    cur.execute("DELETE FROM ONLY services_type WHERE service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid;", ('1cf7bf48-8e61-4aac-afab-0d4e639cb518', '8079671f-d6fd-448d-ace2-d66f6635754d', 'b7c104fc-2286-4f57-af5f-f8c62fe3f262', 'e23dcfcc-dd32-484d-a2a6-bf089017d3d2',))
    cur.execute("DELETE FROM ONLY services_service WHERE id = %s::uuid OR id = %s::uuid OR id = %s::uuid OR id = %s::uuid;", ('1cf7bf48-8e61-4aac-afab-0d4e639cb518', '8079671f-d6fd-448d-ace2-d66f6635754d', 'b7c104fc-2286-4f57-af5f-f8c62fe3f262', 'e23dcfcc-dd32-484d-a2a6-bf089017d3d2',))

    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid;", ('39fdedde-3885-451d-b006-591c3ba36802', '566d9ff9-fd1a-471e-bf67-f4eff5f2d380', '68e5ab29-eaef-41c7-8fb7-1b25f4bc627f', '982b0a47-fd32-4e66-b05b-81bc4200c07e', 'd11b6849-612c-4c35-896a-d225bbaced0a',))

    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid;", ('e3d2b280-cb43-45d9-9e07-4b82b565711d', '55a21da7-ec57-4b4f-ae6f-af1a970191ac', '2312d6ea-73fe-4bce-8f56-b9f83a074e33', '0e6a0e83-a4dc-4385-a2df-a567e68ff3c7', 'd98b4741-0c56-4f4b-83f4-b10fce028b21',))


def technicalStruct(cur):

    #Change to laptop subcategory
    cur.execute("UPDATE ONLY categories_subcategory SET name = 'Laptop Repair' WHERE id = '0bc148f7-d1a1-432d-bb23-6b0191f066b9';")
    cur.execute("UPDATE ONLY services_service SET name = 'PC' WHERE id = '59ede5f7-1c9e-410e-ba35-b1e74243c4cd';")
    cur.execute("UPDATE ONLY services_service SET name = 'Apple', sub_category_id = '0bc148f7-d1a1-432d-bb23-6b0191f066b9' WHERE id = '60352559-9cf1-42e6-9c9d-a9d192fff0fb';")

    cur.execute("SELECT id FROM services_type WHERE service_id = %s::uuid OR service_id = %s::uuid;", ('c9d20c98-61af-4397-80b0-fec70b0e2d2e', '09c98b1a-ef94-4bb6-8392-95bdf5fa762a',))
    desktop_types = cur.fetchall()

    for elem in desktop_types:
        cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", (elem,))
        cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid;", (elem,))

        cur.execute("DELETE FROM ONLY services_service WHERE name = 'Desktop';", (elem,))
        cur.execute("DELETE FROM ONLY categories_subcategory WHERE name = 'Mac Repair';", (elem,))


def fitnessStruct(cur):

    cur.execute("UPDATE ONLY services_service SET name = 'Weight Loss' WHERE name = 'Cardio';")
    cur.execute("UPDATE ONLY services_service SET name = 'Overall Fitness' WHERE name = 'Cardio & Strength';")
    cur.execute("UPDATE ONLY services_service SET name = 'Muscle Gain' WHERE name = 'Strength';")

    #Change mma and boxing from Martial arts to personal trainer subcat
    cur.execute("UPDATE ONLY services_service SET sub_category_id = %s::uuid WHERE id = %s::uuid;", ('be5323ec-094e-42ea-a0c4-e076fe83694b', 'd2778648-d418-4e3d-8a7b-53a3edd796f9',))
    #Delete russian martiuak arts
    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid;", ('c9b325ca-0574-4c3b-84bb-a233bfa05e5a',))
    cur.execute("UPDATE ONLY services_type SET name = '75mins' WHERE name = 'Russian Martial Arts';",)

    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'blah', 'blah', %s::uuid, 0);", (str(uuid.uuid4()), 'c9b325ca-0574-4c3b-84bb-a233bfa05e5a',))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'blah', 'blah', %s::uuid, 0);", (str(uuid.uuid4()), 'c9b325ca-0574-4c3b-84bb-a233bfa05e5a',))

    #Change Boxing into personal training subcat from its own subcat
    cur.execute("UPDATE ONLY services_service SET sub_category_id = %s::uuid WHERE id = %s::uuid;", ('be5323ec-094e-42ea-a0c4-e076fe83694b', '3725eb53-72b9-4185-8efc-d1179895134d',))
    cur.execute("UPDATE ONLY services_service SET name = 'Boxing' WHERE id = %s::uuid;", ('3725eb53-72b9-4185-8efc-d1179895134d',))

    boxing75mins_type = str(uuid.uuid4())
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, '75mins', '75mins', %s::uuid, 0, age(now()));", (boxing75mins_type, '3725eb53-72b9-4185-8efc-d1179895134d',))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'blah', 'blah', %s::uuid, 0);", (str(uuid.uuid4()), boxing75mins_type,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'blah', 'blah', %s::uuid, 0);", (str(uuid.uuid4()), boxing75mins_type,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, 'blah', 'blah', %s::uuid, 0);", (str(uuid.uuid4()), boxing75mins_type,))



    #cur.execute("SELECT id, name FROM services_subtype WHERE service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid;", ('31242bba-c393-4643-910f-b3f084a2135d', '608690e1-f726-49c4-8fd8-64bab0ae569d', 'cf5dfebc-d2b1-44f5-a398-39ad9695abda', 'd2778648-d418-4e3d-8a7b-53a3edd796f9', '3725eb53-72b9-4185-8efc-d1179895134d',))
    #cur.execute("SELECT id FROM services_subtype WHERE service_id = %s::uuid;", ('31242bba-c393-4643-910f-b3f084a2135d',))

    #pertrain_typelist = cur.fetchall()

    #cur.execute("SELECT id, name FROM services_type WHERE service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid OR service_id = %s::uuid;", ('31242bba-c393-4643-910f-b3f084a2135d', '608690e1-f726-49c4-8fd8-64bab0ae569d', 'cf5dfebc-d2b1-44f5-a398-39ad9695abda', 'd2778648-d418-4e3d-8a7b-53a3edd796f9', '3725eb53-72b9-4185-8efc-d1179895134d',))
    def switcheroo(cur, keeptype):

        cur.execute("SELECT id, name FROM services_type WHERE service_id = %s::uuid;", (keeptype,))
        pertrain_typelist = cur.fetchall()


        cur.execute("SELECT id FROM services_subtype WHERE type_id = %s::uuid;", (pertrain_typelist[0][0],))
        subtypelist_1 = cur.fetchall()

        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = %s::uuid;", (subtypelist_1[0], pertrain_typelist[0][0], pertrain_typelist[0][0]))
        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = %s::uuid;", (subtypelist_1[1], pertrain_typelist[0][0], pertrain_typelist[1][0]))
        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid, type_id = %s::uuid WHERE type_id = %s::uuid;", (subtypelist_1[2], pertrain_typelist[0][0], pertrain_typelist[2][0]))

        cur.execute("UPDATE ONLY services_subtype SET name = %s WHERE id = %s::uuid;", (pertrain_typelist[0][1], subtypelist_1[0],))
        cur.execute("UPDATE ONLY services_subtype SET name = %s WHERE id = %s::uuid;", (pertrain_typelist[1][1], subtypelist_1[1],))
        cur.execute("UPDATE ONLY services_subtype SET name = %s WHERE id = %s::uuid;", (pertrain_typelist[2][1], subtypelist_1[2],))
        cur.execute("UPDATE ONLY services_type SET name = 'null' WHERE id = %s::uuid;", (pertrain_typelist[0][0],))

        cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid OR id = %s::uuid;", (pertrain_typelist[1][0], pertrain_typelist[2][0],))
        cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid OR type_id = %s::uuid;", (pertrain_typelist[1][0], pertrain_typelist[2][0],))


    switcheroo(cur, '31242bba-c393-4643-910f-b3f084a2135d') #Cardio
    switcheroo(cur, '608690e1-f726-49c4-8fd8-64bab0ae569d') #Cardio and strength
    switcheroo(cur, 'cf5dfebc-d2b1-44f5-a398-39ad9695abda') #Strength
    switcheroo(cur, 'd2778648-d418-4e3d-8a7b-53a3edd796f9') #MMA
    switcheroo(cur, '3725eb53-72b9-4185-8efc-d1179895134d') #Boxing

    cur.execute("DELETE FROM ONLY services_service WHERE id = %s::uuid;", ('8e5a6aca-582b-43aa-aa29-fa56c589e815',)) #Delete BJJ
    cur.execute("SELECT id FROM services_type WHERE service_id = %s::uuid;", ('8e5a6aca-582b-43aa-aa29-fa56c589e815',))
    bjj_types = cur.fetchall()

    for elem in bjj_types:
        cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid;", (elem,)) #Delete BJJ
        cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", (elem,)) #Delete BJJ
        cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid;", (elem,)) #Delete BJJ


    #Delete martial arts service and old boxing heirarchy
    cur.execute("DELETE FROM ONLY categories_subcategory WHERE name = 'Martial Arts';") #Delete BJJ
    cur.execute("DELETE FROM ONLY categories_subcategory WHERE name = 'Boxing';") #Delete BJJ

    cur.execute("DELETE FROM ONLY services_service WHERE id = %s::uuid;", ('b40125cb-0056-442e-aed8-ac97e06fcca5',))
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", ('4a5c2939-3550-44d7-9417-c8ca09590f0f',))
    cur.execute("DELETE FROM ONLY services_type WHERE id = %s::uuid;", ('a1a57d4e-3d3b-4620-aaa9-e804b3f33398',))
    cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid;", ('4a5c2939-3550-44d7-9417-c8ca09590f0f',))
    cur.execute("DELETE FROM ONLY services_subtype WHERE type_id = %s::uuid;", ('a1a57d4e-3d3b-4620-aaa9-e804b3f33398',))

    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid;", ('4a5c2939-3550-44d7-9417-c8ca09590f0f',))
    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid;", ('a1a57d4e-3d3b-4620-aaa9-e804b3f33398',))

###Add in classes
    classes_subcat_id = str(uuid.uuid4())
    cur.execute("INSERT INTO categories_subcategory VALUES (%s::uuid, now(), now(), "
                "'Classes', 'Classes', '', 0, %s::uuid, False, '#FF79C5E1');", (classes_subcat_id, 'e0901303-1213-4302-9123-9e22f4f9ae1e',))

    crossfit_service_id = str(uuid.uuid4())
    kettlebell_service_id = str(uuid.uuid4())
    zumba_service_id = str(uuid.uuid4())
    spin_service_id = str(uuid.uuid4())

    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, 'Crossfit', %s::uuid, 0);", (crossfit_service_id, classes_subcat_id,))
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, 'Kettlebell', %s::uuid, 0);", (kettlebell_service_id, classes_subcat_id,))
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, 'Zumba', %s::uuid, 0);", (zumba_service_id, classes_subcat_id,))
    cur.execute("INSERT INTO services_service VALUES (%s::uuid, now(), now(), "
                "False, 'Spin', %s::uuid, 0);", (spin_service_id, classes_subcat_id,))

    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, crossfit_service_id,))

    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, kettlebell_service_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '90mins', '90mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))

    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, zumba_service_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '90mins', '90mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))

    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, crossfit_service_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '90mins', '90mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))

    null_type_id = str(uuid.uuid4())
    null_type_id_list.append(null_type_id)
    cur.execute("INSERT INTO services_type VALUES (%s::uuid, now(), now(), "
                "False, 'null', 'null', %s::uuid, 0, age(now()));", (null_type_id, spin_service_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '30mins', '30mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '60mins', '60mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))
    cur.execute("INSERT INTO services_subtype VALUES (%s::uuid, now(), now(), "
                "False, '90mins', '90mins', %s::uuid, 0);", (str(uuid.uuid4()), null_type_id,))


def provservFixErrors(cur):

    myfile = open('tester.csv', 'w', encoding='utf-8')

    cur.execute("SELECT id, subtype_id, type_id FROM providers_providerservice")
    provserv_list = cur.fetchall()
    provserv_list = [item for item in provserv_list if item[1] != None] ##Delete entries with null subtypes

    deleteservlist = ['Foot', 'Manicure', 'Permanent Straightening', 'Professional', 'Mani & Pedi']
    deletetypelist = ['Balayage', 'Ombre', 'Cut throat shave', 'Beard Shave']

    correctlist = []
    errorcount = 0
    for element in provserv_list:

        cur.execute("SELECT name FROM services_type WHERE id = %s::uuid", (element[2],))
        type_name = cur.fetchall()

        cur.execute("SELECT service_id FROM services_type WHERE id = %s::uuid", (element[2],))
        service_id = cur.fetchall()

        cur.execute("SELECT name FROM services_service WHERE id = %s::uuid", (service_id[0],))
        service_name = cur.fetchall()

        cur.execute("SELECT type_id FROM services_subtype WHERE id = %s::uuid AND type_id = %s::uuid", (element[1], element[2],))
        correctentry = cur.fetchall()

        #Strip all whitespace chars from services_type
        cur.execute("SELECT name FROM services_subtype WHERE id = %s::uuid", (element[1],))
        subtypename = cur.fetchall()

        if correctentry == []:          #For incorrect entries

            errorcount = errorcount + 1
            cur.execute("SELECT name, type_id FROM services_subtype WHERE id = %s::uuid", (element[1],))
            badsubtype = cur.fetchall()

            #cur.execute("SELECT id FROM services_subtype WHERE name = %s AND type_id = %s::uuid", (badsubtype[0][0], badsubtype[0][1],))
            cur.execute("SELECT id, name FROM services_subtype WHERE name = %s AND type_id = %s::uuid", (badsubtype[0][0].strip(), element[2],))
            correctsubtype = cur.fetchall()

            if correctsubtype != []:        #If subtype exists with same name and proper type_id, change the subtype_id in provserv to this value
                cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  (correctsubtype[0][0], element[1], element[2],))

        #print(service_name[0][0])
        if service_name[0][0] in deleteservlist:
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  (None, element[1], element[2],))

        if type_name[0][0] in deletetypelist:
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  (None, element[1], element[2],))

        if type_name[0][0] == "Gel" and subtypename[0][0] == "Hands":       ##Set subtype to standard in this case??
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  ('077a2511-34dc-41a3-a77b-df5b22a9dc7c', element[1], element[2],))

        if type_name[0][0] == "Gel" and subtypename[0][0] == "Feet":       ##Set subtype to standard in this case??
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  ('077a2511-34dc-41a3-a77b-df5b22a9dc7c', element[1], element[2],))

        if type_name[0][0] == "Acrylic" and subtypename[0][0] == "Hands":       ##Set subtype to standard in this case??
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  ('4d158272-c543-4796-9a45-6d0df68705c6', element[1], element[2],))

        if type_name[0][0] == "Acrylic" and subtypename[0][0] == "Feet":       ##Set subtype to standard in this case??
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  ('4d158272-c543-4796-9a45-6d0df68705c6', element[1], element[2],))

        if type_name[0][0] == "Express" and subtypename[0][0] != "":       ##Set subtype to standard in this case??
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  (None, element[1], element[2],))

        if type_name[0][0] == "1 hour" and subtypename[0][0] == "Exercise regularly":       ##Set subtype to standard in this case??
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  (None, element[1], element[2],))

        if type_name[0][0] == "Permanent" and subtypename[0][0] == "Highlights":       ##Set subtype to standard in this case??
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  ('fc4db139-49cd-4dab-b7e0-27f9963dc0cb', '907c438e-6b0b-4ec1-b87f-1c677d89424a', element[1], element[2],))

        if type_name[0][0] == "Semi Permanent" and subtypename[0][0] == "Highlights":       ##Set subtype to standard in this case??
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid), type_id = %s::uuid WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  ('fc4db139-49cd-4dab-b7e0-27f9963dc0cb', '907c438e-6b0b-4ec1-b87f-1c677d89424a', element[1], element[2],))

#Individually fix badboys
    #Id = 12613
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  (None, '9dc4a583-67a1-4874-b3ee-c0f0506aa61d', '278ca2bc-110f-4680-b8d6-f230c5aa839d',))
    #11691
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  ('9dc4a583-67a1-4874-b3ee-c0f0506aa61d', '06285d38-67d5-422d-9b17-b4d6a51edf70', '1138fc26-d72f-4bfa-a10d-44a593598e91',))
    #11636
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid) AND type_id = %s::uuid;",  (None, '0ad3c827-ace3-4fbe-b820-ea34e9724762', 'ec6bc85b-959a-447d-8dbf-6a2161bda992',))


def provservPrint(cur):

    myfile = open('tester1.csv', 'w', encoding='utf-8')
    #myfile.write("type (services_subtype) \t\t\t\t type (provserv) \t\t\t subtype \t\t\t provserv \t\t\t service \t\t provserv_id \n")

    cur.execute("SELECT id, subtype_id, type_id FROM providers_providerservice")
    provserv_list = cur.fetchall()
    print("Number of provserv entries: " + str(len(provserv_list)))

    #Delete all elements in list with no subtype
    provserv_list = [item for item in provserv_list if item[1] != None]
    print("Number of provserv entries with subtypes: " + str(len(provserv_list)))


    for element in provserv_list:

        ####***type_id = correct type_id - i.e. new type_id
        cur.execute("SELECT type_id FROM services_subtype WHERE id = %s::uuid", (element[1],))
        type_id = cur.fetchall()

        if len(type_id) < 1:
            type_id = None
        else:
            type_id = str(type_id[0][0])

    ##For each subtype print correct type and type used in provserv
        if type_id != element[2]:
            #myfile.write(str(type_id) + "\t\t\t" + str(element[2]) + "\t" + str(element[1]) + "\t" + str(element[0]) + "\n")
            pass

    ##For each subtype print out name and prev/new typenames
        cur.execute("SELECT name FROM services_subtype WHERE id = %s::uuid", (element[1],))
        subtypename = cur.fetchall()

        cur.execute("SELECT name FROM services_type WHERE id = %s::uuid", (type_id,))
        wrongtypename = cur.fetchall()

        cur.execute("SELECT name, service_id FROM services_type WHERE id = %s::uuid", (element[2],))
        oldtypename = cur.fetchall()
#new->wrong, old->correct
        cur.execute("SELECT name FROM services_service WHERE id = %s::uuid", (oldtypename[0][1],))
        oldserviceename = cur.fetchall()

        cur.execute("SELECT service_id FROM services_type WHERE id = %s::uuid", (type_id,))
        correctserviceid = cur.fetchall()

        cur.execute("SELECT name FROM services_service WHERE id = %s::uuid", (correctserviceid[0],))
        correctservicename = cur.fetchall()

        if subtypename == wrongtypename:
            cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (None, element[1],))


        #if newtypename[0][0] != oldtypename[0][0]:
        if type_id != element[2]:

            myfile.write("Error -  service: " + str(oldserviceename[0][0] + " \t type: " + str(oldtypename[0][0]) +  " \t subtype: " + str(subtypename[0][0]) + " \t providers_providerservice_id: " + str(element[0]) + "\n"))

            if correctserviceid[0][0] == oldtypename[0][1]:   ###have to use ids because some services have same name as types
                #myfile.write("Subtype not exist - provserv service: " + str(correctservicename[0][0]) + "  type: " + str(oldtypename[0][0]) + "  subtype: " + str(subtypename[0][0]) + "\n")
                cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = %s::uuid WHERE subtype_id = %s::uuid;", (None, element[1],))


def fixFuckup(cur):

    #######Need to catch and delete null subtypes that shouldnt be null subtypes
    myfile = open('badsubtypes.csv', 'w', encoding='utf-8')

    cur.execute("SELECT id, subtype_id, type_id FROM providers_providerservice")
    provserv_list = cur.fetchall()

    cur.execute("SELECT id FROM services_type")
    type_list = cur.fetchall()

    empty_subtype_errorlist = []

    for elem in type_list:
        cur.execute("SELECT id FROM services_subtype WHERE type_id = %s::uuid;", (elem,))
        subbers = cur.fetchall()

    ##This part finds and deletes provserv entries which have empty subtypes_ids that should have subtype_ids
        if len(subbers) >= 1:
            cur.execute("SELECT type_id, subtype_id, id FROM providers_providerservice WHERE type_id = %s::uuid;", (elem,))
            #cur.execute("SELECT type_id, subtype_id FROM providers_providerservice WHERE type_id = %s AND subtype_id = %s::uuid;", (elem, None))
            item = cur.fetchall()

            if item != []:

                for i in range(0, len(item)):

                    cur.execute("SELECT name, service_id FROM services_type WHERE id = %s::uuid;", (item[i][0],))
                    typename = cur.fetchall()
                    cur.execute("SELECT name FROM services_service WHERE id = %s::uuid;", (typename[0][1],))
                    servicename = cur.fetchall()

                    if str(servicename[0][0]) == "Vinyasa" and str(typename[0][0]) == "1 hour":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('1c1106ae-fb57-4e50-9d93-37e551a9f9a5', item[i][2],))

                    if str(servicename[0][0]) == "Power" and str(typename[0][0]) == "1 hour":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('e49b6724-3d19-402f-9d53-e6285bbb34c8', item[i][2],))

                    if str(servicename[0][0]) == "Power" and str(typename[0][0]) == "1.5 hours":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('32bcf527-f1c6-442a-8db9-16a88f1d4337', item[i][2],))

                    if str(servicename[0][0]) == "Classical" and str(typename[0][0]) == "1 hour":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('9dc4a583-67a1-4874-b3ee-c0f0506aa61d', item[i][2],))

                    if str(servicename[0][0]) == "Wash & Blowave" and str(typename[0][0]) == "Wash only":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('5ca894fb-0e6b-4ba8-8e13-0c8102077c2e', item[i][2],))

                    if str(servicename[0][0]) == "Wash & Blowave" and str(typename[0][0]) == "Blowave only":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('d6311a2e-586a-404d-993d-4204f14afef5', item[i][2],))

                    if str(servicename[0][0]) == "Pamper" and str(typename[0][0]) == "Foot Bath":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('b4fbf730-4c60-416f-8e15-dc9ecedfd71e', item[i][2],))

                    if str(servicename[0][0]) == "Shave" and str(typename[0][0]) == "Beard trim":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('57473265-df0a-4791-aecb-fada428bad4b', item[i][2],))

                    if str(servicename[0][0]) == "Facial" and str(typename[0][0]) == "Exfoliating":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('16bbd9f8-942c-4d8b-ae5c-8fe9d779f927', item[i][2],))

                    if str(servicename[0][0]) == "Tailor" and str(typename[0][0]) == "Suit":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('efffbb9c-bf71-4310-8d8e-8c85e423bee8', item[i][2],))

                    if str(servicename[0][0]) == "File & paint" and str(typename[0][0]) == "Standard polish":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('7e9cdb8c-798e-45b4-aa62-e324b48c27da', item[i][2],))

                    if str(servicename[0][0]) == "Vinyasa" and str(typename[0][0]) == "1.5 hours":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('865171e9-4d34-45f8-bd7f-1edea00eb05e', item[i][2],))

                    if str(servicename[0][0]) == "Full set" and str(typename[0][0]) == "Gel":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('077a2511-34dc-41a3-a77b-df5b22a9dc7c', item[i][2],))

                    if str(servicename[0][0]) == "Hatha" and str(typename[0][0]) == "1 hour":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('45a5f6ff-734c-4689-8902-7e4382749ad6', item[i][2],))

                    if str(servicename[0][0]) == "Occasional Hair" and str(typename[0][0]) == "Blowdry":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('25aca80d-5b0c-4ec8-a097-5d46c685ba51', item[i][2],))

                    if str(servicename[0][0]) == "Full set" and str(typename[0][0]) == "Acrylic":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('4d158272-c543-4796-9a45-6d0df68705c6', item[i][2],))

                    if str(servicename[0][0]) == "Tailor" and str(typename[0][0]) == "Skirt":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('bcb2c6e3-5880-4f27-adf8-9c040f15590a', item[i][2],))

                    if str(servicename[0][0]) == "Hatha" and str(typename[0][0]) == "1.5 hours":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('c4eec14b-8d06-4bb5-a14c-e071d561a8ec', item[i][2],))

                    if str(servicename[0][0]) == "Restoration" and str(typename[0][0]) == "Zip/ velcro/ strap repair":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('041e339f-c50d-47e4-a975-bd5c73cc3f0e', item[i][2],))

                    if str(servicename[0][0]) == "Tailor" and str(typename[0][0]) == "Pant":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('8248ed5d-ac7d-4919-83f4-205862d76626', item[i][2],))

                    if str(servicename[0][0]) == "Occasional Hair" and str(typename[0][0]) == "Hair up":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('e8a55b9a-cd31-481a-9a8a-71b54eed26de', item[i][2],))

                    if str(servicename[0][0]) == "Contemporary" and str(typename[0][0]) == "1 hour":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('a4d32973-2f15-4a8a-a683-382d3680f26a', item[i][2],))

                    if str(servicename[0][0]) == "Reflexology" and str(typename[0][0]) == "30mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('aaa654cf-4f13-40f7-8cf8-1c745b87678a', item[i][2],))

                    if str(servicename[0][0]) == "Reflexology" and str(typename[0][0]) == "60mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('5c183f0d-a1dc-4d98-ada8-3c04b2bc00ed', item[i][2],))

                    if str(servicename[0][0]) == "Reflexology" and str(typename[0][0]) == "75mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('6d74c279-b368-4fee-b919-1a4ad718ce96', item[i][2],))

                    if str(servicename[0][0]) == "Relaxation" and str(typename[0][0]) == "60mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('38cac203-55f4-484f-b211-3b7db2f4b8e1', item[i][2],))

                    if str(servicename[0][0]) == "Cut" and str(typename[0][0]) == "Hair Reshape":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('caf69074-fea9-4e05-a161-4154948f62d5', item[i][2],))

                    if str(servicename[0][0]) == "Relaxation" and str(typename[0][0]) == "120mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('fab82825-42aa-46ee-9ba6-351fdbd007e1', item[i][2],))

                    if str(servicename[0][0]) == "Relaxation" and str(typename[0][0]) == "30mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('07076a6f-804a-470c-99c4-f3c79381697e', item[i][2],))

                    if str(servicename[0][0]) == "Remedial" and str(typename[0][0]) == "30mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('769f484d-d6c0-4500-992c-e960767f6d95', item[i][2],))

                    if str(servicename[0][0]) == "Relaxation" and str(typename[0][0]) == "90mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('5fbe66a1-e8a5-4d41-a627-277c87176706', item[i][2],))

                    if str(servicename[0][0]) == "Personal Shopper" and str(typename[0][0]) == "Consultation & personal shop":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('a3c99d52-5688-436a-9cc3-cd94efaacc31', item[i][2],))

                    if str(servicename[0][0]) == "Group session" and str(typename[0][0]) == "60mins":
                        cur.execute("DELETE FROM ONLY providers_providerservice WHERE id = %s;", (item[i][2],))

                    if str(servicename[0][0]) == "Facial" and str(typename[0][0]) == "Extraction":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('3bd2789e-c519-46f6-bc57-729fd3126423', item[i][2],))

                    if str(servicename[0][0]) == "Facial" and str(typename[0][0]) == "Rejuvenate":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('89765265-cd65-44c5-ba32-f14e27e1dedf', item[i][2],))

                    if str(servicename[0][0]) == "Facial" and str(typename[0][0]) == "Pore cleansing":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('8696649b-43a1-4486-8b9e-16d3f1c897e4', item[i][2],))

                    if str(servicename[0][0]) == "Facial" and str(typename[0][0]) == "Anti Aging":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('2acfae23-7100-4d38-aee4-7b021b6531f6', item[i][2],))

                    if str(servicename[0][0]) == "Spray tan" and str(typename[0][0]) == "Full body":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('d3a1ad0c-36a7-4fa4-b8ca-3b12ea751c48', item[i][2],))

                    if str(servicename[0][0]) == "MMA" and str(typename[0][0]) == "45mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('ad00e53d-3fd2-4d4e-8dce-377025bd2bfb', item[i][2],))

                    if str(servicename[0][0]) == "MMA" and str(typename[0][0]) == "60mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('bf78a19c-88ae-4a0c-abae-ab80c49d0c49', item[i][2],))

                    if str(servicename[0][0]) == "Cardio & Strength" and str(typename[0][0]) == "45mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('82534f15-416d-4438-8ae7-cba684cb85bf', item[i][2],))

                    if str(servicename[0][0]) == "Cardio & Strength" and str(typename[0][0]) == "60mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('287fa56b-e7db-4270-b4d1-19674f1a6416', item[i][2],))

                    if str(servicename[0][0]) == "Cardio" and str(typename[0][0]) == "45mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('1dc776bd-be55-4129-8aaf-e75cac2acd8f', item[i][2],))

                    if str(servicename[0][0]) == "Brazilian Jiu Jitsu" and str(typename[0][0]) == "60mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('e2d136a0-1283-4ad2-8b65-81cc69788051', item[i][2],))

                    if str(servicename[0][0]) == "Private session" and str(typename[0][0]) == "60mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('36c8cd64-0e59-438d-9c7f-1437c03118e0', item[i][2],))

                    if str(servicename[0][0]) == "Brazilian Jiu Jitsu" and str(typename[0][0]) == "45mins":
                        cur.execute("UPDATE providers_providerservice SET subtype_id = %s::uuid WHERE id = %s;", ('18d2066e-40b4-4d2e-b114-359b7ae02540', item[i][2],))


            cur.execute("SELECT type_id, subtype_id, id FROM providers_providerservice WHERE type_id = %s::uuid;", (elem,))
            #cur.execute("SELECT type_id, subtype_id FROM providers_providerservice WHERE type_id = %s AND subtype_id = %s::uuid;", (elem, None))
            item = cur.fetchall()
            if item != []:

                for i in range(0, len(item)):

                    if item[i][1] == None:
                        print(item[i])
                        #cur.execute("DELETE FROM ONLY providers_providerservice WHERE id = %s;", (item[i][2],))
                        empty_subtype_errorlist.append(item[i][2])

                        myfile.write(str(servicename[0][0]) + "   " + str(typename[0][0]) + "   " + str(item[i][2]) + "\n")



        #if elem[1] != []
    print(len(empty_subtype_errorlist))

    error_list = 0

    for element in provserv_list:

        ####***type_id = correct type_id - i.e. new type_id
        cur.execute("SELECT type_id FROM services_subtype WHERE id = %s::uuid", (element[1],))
        type_id = cur.fetchall()
        error = 0

        if len(type_id) < 1:
            error = 1
            #print("no type id for this subtype")

        # if len(type_id) > 1:
        #     error = 1

        if len(type_id) == 1:
            type_id = str(type_id[0][0])

    ##For each subtype print correct type and type used in provserv
        if type_id != element[2]:
            error = 1
            #myfile.write(str(type_id) + "\t\t\t" + str(element[2]) + "\t" + str(element[1]) + "\t" + str(element[0]) + "\n")

        # if error == 1:
        #     cur.execute("DELETE FROM ONLY providers_providerservice WHERE subtype_id = %s::uuid;", (element[1],))


        error_list = error_list + error


    cur.execute("SELECT subtype_id FROM providers_providerservice WHERE type_id = %s::uuid;", ('907c438e-6b0b-4ec1-b87f-1c677d89424a',))


def preFuckup(cur):

#Laser
    cur.execute("SELECT id FROM services_type WHERE service_id = %s::uuid;", ('cb47de42-f674-4733-9413-a0edee906a5d',))
    lasertypes = cur.fetchall()
    for elem in lasertypes:
        cur.execute("SELECT id FROM services_subtype WHERE type_id = %s::uuid AND name = 'Normal Skin';", (elem,))
        normal_subtype = cur.fetchall()
        cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE type_id = %s::uuid;",  (normal_subtype[0], elem[0],))

#Pregnancy
    cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid OR type_id = %s::uuid OR type_id = %s::uuid;", ('2c96a430-66d5-4856-9f19-fe4bb8329cc2', '443a2886-8b30-474a-9803-794553e6a7f9', 'f559ada4-ae8f-4951-a2f5-1a3d99ec3e74',))


#Body Scrub
    #cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid AND subtype_id  = %s::uuid;", ('c6a011e9-6e30-490a-812e-fbc168e4b597', '2fd0523f-7c1b-4932-97aa-0ca7760e9fd7',))
    #cur.execute("DELETE FROM ONLY providers_providerservice WHERE type_id = %s::uuid AND subtype_id  = %s::uuid;", ('c6a011e9-6e30-490a-812e-fbc168e4b597', '2fd0523f-7c1b-4932-97aa-0ca7760e9fd7',))
    buffer_Type_id = str(uuid.uuid4())
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (buffer_Type_id, '2fd0523f-7c1b-4932-97aa-0ca7760e9fd7',))#90mins temporarily move
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('e16d53c0-7434-4f7f-892e-5f0b3b78cc1b', 'c6a011e9-6e30-490a-812e-fbc168e4b597',))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('c6a011e9-6e30-490a-812e-fbc168e4b597', buffer_Type_id,))
#Body Wrap
    buffer_Type_id = str(uuid.uuid4())
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (buffer_Type_id, '2a9161f4-4125-45f1-a978-53da517619a0',))#90mins temporarily move
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('4b5230ab-9afe-4cc3-ba1b-28973bb16a05', 'c8004de4-d4e2-4e49-870f-244b42872c7c',))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('c8004de4-d4e2-4e49-870f-244b42872c7c', buffer_Type_id,))

#Shellac
    buffer_Type_id = str(uuid.uuid4())
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (buffer_Type_id, '3e4f2831-58c1-4a95-97dc-72194a4214a7',))#90mins temporarily move
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('aabb9832-9eea-4bf8-b66b-f31d4b788a91', '006c9559-58b7-4466-92b1-cccc562b6178',))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('006c9559-58b7-4466-92b1-cccc562b6178', buffer_Type_id,))

#Standard polish
    buffer_Type_id = str(uuid.uuid4())
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (buffer_Type_id, '0f537b30-8afd-420a-adb7-0a8d04eebca5',))#90mins temporarily move
    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('ec6bc85b-959a-447d-8dbf-6a2161bda992', '1c68dd6b-6942-4002-b98f-5a244a2350c0',))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('1c68dd6b-6942-4002-b98f-5a244a2350c0', buffer_Type_id,))

#Regrowth -> highlights ''
    buffer_Type_id_half = str(uuid.uuid4())
    buffer_Type_id_quart = str(uuid.uuid4())
    buffer_Type_id_part = str(uuid.uuid4())
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (buffer_Type_id_half, '82ac94ba-02c0-4c83-bc6f-b09ac4e3b552',))#90mins temporarily move
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (buffer_Type_id_quart, 'c56b2ea1-e94d-4b99-9432-db2dc18c0a72',))#90mins temporarily move
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (buffer_Type_id_part, 'cb48de88-7c1f-41f2-9717-5f8e889d010a',))#90mins temporarily move

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('55535dba-8434-4c20-9d58-d1e35896e233', '9c07a9c5-05a3-4fb5-bc74-c5411df8ea50',))

    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('9c07a9c5-05a3-4fb5-bc74-c5411df8ea50', buffer_Type_id_half,))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('9c07a9c5-05a3-4fb5-bc74-c5411df8ea50', buffer_Type_id_quart,))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('9c07a9c5-05a3-4fb5-bc74-c5411df8ea50', buffer_Type_id_part,))

#Haircut
    buffer_Type_id_short = str(uuid.uuid4())
    buffer_Type_id_long = str(uuid.uuid4())
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (buffer_Type_id_short, '53f744da-c6c3-437f-aa88-7bd819be36b8',))#90mins temporarily move
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE subtype_id = (%s::uuid);",  (buffer_Type_id_long, 'ae921c7c-6324-4acc-b238-91e5c02988d6',))#90mins temporarily move

    cur.execute("UPDATE ONLY providers_providerservice SET subtype_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('ba636253-b9e1-4f7d-84a9-7bd7593a26ff', 'a94a119a-4136-4ea9-8abf-e69f2ae93b7b',))

    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('a94a119a-4136-4ea9-8abf-e69f2ae93b7b', buffer_Type_id_short,))
    cur.execute("UPDATE ONLY providers_providerservice SET type_id = (%s::uuid) WHERE type_id = (%s::uuid);",  ('a94a119a-4136-4ea9-8abf-e69f2ae93b7b', buffer_Type_id_long,))


def testo(cur):

    myfile = open('test.csv', 'w', encoding='utf-8')

    subtype_name_list = []
    type_name_list = []
    service_name_list = []
    subcategory_name_list = []

    cur.execute("SELECT id FROM providers_providerservice")
    provserv_id_list = cur.fetchall()

    cur.execute("SELECT subtype_id FROM providers_providerservice")
    subtype_id_list = cur.fetchall()

    for elem in subtype_id_list:

        cur.execute("SELECT name FROM services_subtype WHERE id = %s::uuid;", (elem,))
        subtype_name = cur.fetchone()
        if subtype_name == None:
            subtype_name = ['']

        subtype_name_list.append(subtype_name[0])


    cur.execute("SELECT type_id FROM providers_providerservice")
    type_id_list = cur.fetchall()

    i = 0
    # #create arrays of table ids and then find their names
    for elem in type_id_list:  #create array of service ids

        #Type
        cur.execute("SELECT name FROM services_type WHERE id = %s::uuid;", (elem,))
        type_name = cur.fetchone()

        if type_name == None:
            type_name = ['']

        type_name_list.append(type_name[0])
        #Service
        cur.execute("SELECT service_id FROM services_type WHERE id = %s::uuid;", (elem,))
        service_id = cur.fetchone()
        cur.execute("SELECT name FROM services_service WHERE id = %s::uuid;", (service_id,))
        service_name = cur.fetchone()
        if service_name == None:
            service_name = ['']
        service_name_list.append(service_name[0])
        #Subcat
        cur.execute("SELECT sub_category_id FROM services_service WHERE id = %s::uuid;", (service_id,))
        subcategory_id = cur.fetchone()
        cur.execute("SELECT name FROM categories_subcategory WHERE id = %s::uuid;", (subcategory_id,))
        subcategory_name = cur.fetchone()
        if subcategory_name == None:
            subcategory_name = ['']
        subcategory_name_list.append(subcategory_name[0])

        i = i + 1

    return provserv_id_list, subtype_name_list, type_name_list, service_name_list, subcategory_name_list


def restructure():

    conn = psycopg2.connect("dbname=check user=postgres password=Chozunone")
    cur = conn.cursor()

    cur.execute("UPDATE services_subtype SET name = 'Back & Shoulders' WHERE name = 'Back & shoulders';")
    cur.execute("UPDATE services_subtype SET name = 'Half Body' WHERE name = 'Half body';")
    cur.execute("UPDATE services_subtype SET name = 'Full Body' WHERE name = 'Full body';")
    cur.execute("UPDATE services_subtype SET name = 'Foot' WHERE name = 'Feet only';")
    cur.execute("UPDATE services_subtype SET name = 'Foot' WHERE name = 'Feet Only';")

    old_provserv_id_list, old_subtype_name_list, old_type_name_list, old_service_name_list, old_subcategory_name_list = testo(cur)

    provservFixErrors(cur)
    preFuckup(cur)
    fixFuckup(cur)
    provservPrint(cur)


    styleStruct(cur)
    wellnessStruct(cur)
    groomingStruct(cur)
    localStruct(cur)
    technicalStruct(cur)
    fitnessStruct(cur)
    sqltest(cur)


    new_provserv_id_list, new_subtype_name_list, new_type_name_list, new_service_name_list, new_subcategory_name_list = testo(cur)

    myfile = open('test.txt', 'w', encoding='utf-8')
    print(len(old_subcategory_name_list))
    print(len(new_subcategory_name_list))
    myfile.write("Provserv id       Old subcat name        New subcat name \n")

    for i in range(0, len(old_provserv_id_list)):

        for j in range(0, len(new_provserv_id_list)):

            if old_provserv_id_list[i] == new_provserv_id_list[j]:
                #if old_type_name_list[i] != new_type_name_list[j]:
                if str(old_type_name_list[i]) == str(new_subtype_name_list[j]) and str(old_subtype_name_list[i]) == str(new_type_name_list[j]):
                    pass

                elif str(old_type_name_list[i]) == str(new_type_name_list[j]) and str(old_subtype_name_list[i]) == str(new_subtype_name_list[j]):
                    pass

                elif str(old_type_name_list[i]) == str(new_type_name_list[j]) and str(old_subtype_name_list[i]) == 'Long Length' and str(new_subtype_name_list[j]) == 'Senior Stylist':
                    pass

                elif str(old_type_name_list[i]) == str(new_type_name_list[j]) and str(old_subtype_name_list[i]) == 'Short Length' and str(new_subtype_name_list[j]) == 'Junior Stylist':
                    pass

                elif str(old_type_name_list[i]) == str(new_type_name_list[j]) and str(old_subtype_name_list[i]) == 'Medium Length' and str(new_subtype_name_list[j]) == 'Standard Stylist':
                    pass

                else:
                    myfile.write(str(old_provserv_id_list[i][0]) + "    " + str(old_service_name_list[i]) + " -> " + str(old_type_name_list[i]) + "    " + str(new_service_name_list[j]) + " -> " + str(new_type_name_list[j]) + "\n")


    conn.commit()


restructure()
