"""This module contains data structures for historical events and personality tests.
"""

# historical events data for the application
HISTORICAL_EVENTS = {
    "1453": {
        "event": "İstanbul'un Fethi",
        "date": "29 Mayıs 1453",
        "characters": ["Fatih Sultan Mehmet", "Konstantin XI", "Halil Paşa"],
        "setting": "Konstantinopolis surları önünde top sesleri yankılanıyor. Fatih Sultan Mehmet son hazırlıkları gözden geçiriyor.",
        "opening": "Şafak vakti, sur dibindeki çadırda Fatih Sultan Mehmet haritaya bakıyor ve sana dönerek diyor: 'Bu gece tarih yazılacak. Sen bu kutsal anda bizimle misin?'"
    },
    "1071": {
        "event": "Malazgirt Savaşı",
        "date": "26 Ağustos 1071",
        "characters": ["Sultan Alparslan", "Romanos IV", "Nizam-ül Mülk"],
        "setting": "Malazgirt ovalarında iki büyük ordu karşı karşıya. Sultan Alparslan beyaz kaftan giymiş, attan iniyor.",
        "opening": "Sultan Alparslan kılıcını çıkararak toprağa saplar ve sana bakar: 'Eğer şehit düşersem, oğlum Melikşah'a bu kılıcı götür. Sen bu tarihi anın şahidi olmaya hazır mısın?'"
    },
    "1789": {
        "event": "Fransız Devrimi",
        "date": "14 Temmuz 1789",
        "characters": ["Robespierre", "Danton", "Marat"],
        "setting": "Paris sokaklarında barikatlar kuruluyor, halk Bastille'e yürüyor. Robespierre bir kahvehane köşesinde planlar yapıyor.",
        "opening": "Robespierre gözlerinin içine bakıyor ve soruyor: 'Sen kimin tarafındasın? Kralın mı, yoksa halkın mı? Bu devrim için kanın akacak!'"
    },
    "1492": {
        "event": "Amerika'nın Keşfi",
        "date": "12 Ekim 1492",
        "characters": ["Kristof Kolomb", "Martin Pinzon", "Rodrigo de Triana"],
        "setting": "Santa Maria gemisinin güvertesinde, uzun deniz yolculuğunun ardından nihayet kara görünüyor.",
        "opening": "Kolomb geminin direğinde duruyor ve sana dönerek diyor: 'İşte! Yeni bir dünya! Sen bu tarihi keşfin tanığı olmak ister misin?'"
    },
    "1299": {
        "event": "Osmanlı Devleti'nin Kuruluşu",
        "date": "1299",
        "characters": ["Osman Gazi", "Şeyh Edebali", "Malhun Hatun"],
        "setting": "Söğüt'te küçük bir beylik kurulmaya çalışılıyor. Osman Gazi çadırında gelecek planları yapıyor.",
        "opening": "Osman Gazi rüyasını anlatıyor: 'Göğsümden bir ağaç çıktı, dalları tüm dünyayı kapladı. Sen bu rüyanın gerçek olacağına inanır mısın?'"
    }
}

# personality test data for the application

PERSONALITY_TEST = {
    "questions": [
        {
            "question": "Yeni bir proje başlatırken hangi yaklaşımı tercih edersiniz?",
            "options": [
                {"text": "Detaylı plan yapar, her aşamayı önceden hesaplarım",
                 "traits": {"conscientiousness": 2, "openness": 1}},
                {"text": "Genel bir fikir ile başlar, yol boyunca şekillendiriririm",
                 "traits": {"openness": 2, "conscientiousness": -1}},
                {"text": "Başkalarının fikirlerini dinler, ortak karar veririm",
                 "traits": {"agreeableness": 2, "extraversion": 1}},
                {"text": "İçgüdülerime güvenir, spontane hareket ederim", "traits": {"neuroticism": 1, "openness": 1}}
            ]
        },
        {
            "question": "Karşılaştığınız zorluklar karşısında nasıl tepki verirsiniz?",
            "options": [
                {"text": "Analitik düşünür, sistematik çözümler ararım",
                 "traits": {"conscientiousness": 2, "neuroticism": -1}},
                {"text": "Yaratıcı ve sıra dışı yöntemler denerim", "traits": {"openness": 2, "conscientiousness": -1}},
                {"text": "Diğer insanlardan yardım ve tavsiye alırım",
                 "traits": {"agreeableness": 2, "extraversion": 1}},
                {"text": "Duygusal yaklaşır, içsel motivasyonuma güvenirim",
                 "traits": {"neuroticism": 1, "agreeableness": 1}}
            ]
        },
        {
            "question": "İdeal bir akşam nasıl geçirirsiniz?",
            "options": [
                {"text": "Kitap okuyarak veya öğrendiğim konuları derinleştirerek",
                 "traits": {"openness": 2, "extraversion": -1}},
                {"text": "Arkadaşlarımla sohbet ederek, deneyimlerimi paylaşarak",
                 "traits": {"extraversion": 2, "agreeableness": 1}},
                {"text": "Sanat, müzik veya yaratıcı aktivitelerle",
                 "traits": {"openness": 2, "conscientiousness": -1}},
                {"text": "Düzenli rutinlerimi sürdürerek, planlarımı gözden geçirerek",
                 "traits": {"conscientiousness": 2, "extraversion": -1}}
            ]
        },
        {
            "question": "Liderlik tarzınızı nasıl tanımlarsınız?",
            "options": [
                {"text": "Vizyon sahibi, ilham verici ve yenilikçi", "traits": {"openness": 2, "extraversion": 1}},
                {"text": "Disiplinli, adaletli ve kurallara bağlı",
                 "traits": {"conscientiousness": 2, "agreeableness": 1}},
                {"text": "Empati kuran, destekleyici ve işbirlikçi", "traits": {"agreeableness": 2, "extraversion": 1}},
                {"text": "Kararlı, tutarlı ancak esnek", "traits": {"conscientiousness": 1, "neuroticism": -1}}
            ]
        },
        {
            "question": "Hangi tür bilgi sizi en çok cezbeder?",
            "options": [
                {"text": "Bilimsel keşifler ve teknolojik yenilikler",
                 "traits": {"openness": 2, "conscientiousness": 1}},
                {"text": "Tarihsel olaylar ve kültürel gelişmeler", "traits": {"openness": 1, "conscientiousness": 1}},
                {"text": "İnsan ilişkileri ve sosyal dinamikler", "traits": {"agreeableness": 2, "extraversion": 1}},
                {"text": "Felsefe ve yaşamın anlamı üzerine düşünceler", "traits": {"openness": 2, "neuroticism": 1}}
            ]
        }
    ],
    "characters": [
        {
            "name": "Leonardo da Vinci",
            "traits": {"openness": 10, "conscientiousness": 7, "extraversion": 5, "agreeableness": 6, "neuroticism": 4},
            "description": "Çok yönlü deha, sanat ve bilimi birleştiren yaratıcı vizyon",
            "quote": "Öğrenme bizim yaşadığımız sürece devam eder."
        },
        {
            "name": "Fatih Sultan Mehmet",
            "traits": {"openness": 8, "conscientiousness": 9, "extraversion": 8, "agreeableness": 5, "neuroticism": 3},
            "description": "Stratejik düşünür, kararlı lider ve vizyon sahibi fatih",
            "quote": "Ya İstanbul'u alırım, ya da İstanbul beni alır."
        },
        {
            "name": "Mevlana",
            "traits": {"openness": 9, "conscientiousness": 6, "extraversion": 6, "agreeableness": 10, "neuroticism": 2},
            "description": "Sevgi dolu, hoşgörülü ve hakikati arayan mutasavvıf",
            "quote": "Sevgi yolculuğu, bizi kendimize götürür."
        },
        {
            "name": "Ibn Khaldun",
            "traits": {"openness": 9, "conscientiousness": 8, "extraversion": 4, "agreeableness": 7, "neuroticism": 3},
            "description": "Sosyal bilimcı, tarihçi ve medeniyet analisti",
            "quote": "Tarih, toplumların yükseliş ve çöküş kanunlarını öğretir."
        },
        {
            "name": "Yunus Emre",
            "traits": {"openness": 8, "conscientiousness": 5, "extraversion": 7, "agreeableness": 9, "neuroticism": 4},
            "description": "Halkın ozanı, sevgi ve kardeşlik şairi",
            "quote": "Yaratılanı severiz, Yaratan'dan ötürü."
        },
        {
            "name": "Sultan Alparslan",
            "traits": {"openness": 6, "conscientiousness": 9, "extraversion": 7, "agreeableness": 6, "neuroticism": 2},
            "description": "Adil hükümdar, stratejik komutan ve devlet adamı",
            "quote": "Adalet, saltanatın temelidir."
        },
        {
            "name": "İbn Sina (Avicenna)",
            "traits": {"openness": 10, "conscientiousness": 8, "extraversion": 4, "agreeableness": 7, "neuroticism": 3},
            "description": "Hekim, filozof ve bilim insanı",
            "quote": "Bilgi, onu arayan ve emek verenlerindir."
        },
        {
            "name": "Akşemseddin",
            "traits": {"openness": 8, "conscientiousness": 8, "extraversion": 5, "agreeableness": 8, "neuroticism": 2},
            "description": "Bilgin, mutasavvıf ve Fatih'in hocası",
            "quote": "İlim öğren, kendini bil."
        }
    ]
}