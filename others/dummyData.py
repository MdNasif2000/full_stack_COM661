import random , json

def generate_data(num):
    towns = ['London','Liverpool', 'Camden', 'Ilford','Manchester','Richmond','Portsmouth', 'Worthing',
             'Belfast','Tower Hill']
    
    reviews_text = ['Good service', 'Poor service', 'Would not recommend', 'Could be better', 'Not worth the price', 'Excellent product',
                    'Rude staff', 'Friendly staff', 'Good place, Worth the visit']
    
    usernames = ['user1','user2','user3','user4','user5','user6','user7','user8','user9','user0',]
    
    business_list =[]
    
    for i in range(1,num + 1):
        # name = "Biz" + str(i)
        # town = random.choice(towns)
        #rating = random.randint(1,5)
        reviews =[]
        review_id_counter = 1
        for _ in range(random.randint(2,3)):
            #username = random.choice(usernames)
            #comment = random.choice(reviews_text)
            #stars = random.randint(1,5)
            reviews.append(
                {
                    "id":review_id_counter ,
                    "username" : random.choice(usernames),
                    "comment" : random.choice(reviews_text),
                    "stars": random.randint(1,5),
                })
            review_id_counter += 1
        business_list.append({
            "name": "Biz" + str(i),
            "town": random.choice(towns),
            "rating": random.randint(1,5),
            "reviews": reviews,
        })
    return business_list
            
businesses = generate_data(100)

with open("data.json","w") as fout:
    json.dump(businesses, fout , indent=4)