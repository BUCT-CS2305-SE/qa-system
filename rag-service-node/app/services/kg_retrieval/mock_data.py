MOCK_RESULTS = {
    "artifact_museum_query": [
        {
            "artifact": "Admonitions Scroll",
            "museum": "The British Museum",
            "source_name": "The British Museum",
            "source_url": "https://www.britishmuseum.org/collection",
        }
    ],
    "artifact_period_query": [
        {
            "artifact": "Bronze Galloping Horse",
            "dynasty": "Eastern Han",
            "source_name": "Gansu Provincial Museum",
            "source_url": "https://example.org/artifact/bronze-horse",
        }
    ],
    "artifact_material_query": [
        {
            "artifact": "Bronze Galloping Horse",
            "material": "Bronze",
            "source_name": "Cultural Heritage KG",
            "source_url": "https://example.org/artifact/bronze-horse",
        }
    ],
    "artifact_type_query": [
        {
            "artifact": "Tea Bowl and Dish",
            "type": "Ceramic",
            "source_name": "Art Institute of Chicago",
            "source_url": "https://www.artic.edu/collection",
        }
    ],
    "artifact_description_query": [
        {
            "artifact": "Tea Bowl and Dish",
            "description": "A ceramic tea bowl and dish from the Chinese collection at the Art Institute of Chicago, featuring delicate glaze and refined craftsmanship typical of the period.",
            "source_name": "Art Institute of Chicago",
            "source_url": "https://www.artic.edu/collection",
        }
    ],
    "artifact_dimensions_query": [
        {
            "artifact": "Tea Bowl and Dish",
            "dimensions": "Diameter 15.2cm, Height 6.3cm",
            "source_name": "Art Institute of Chicago",
            "source_url": "https://www.artic.edu/collection",
        }
    ],
    "painting_author_query": [
        {
            "artifact": "Along the River During the Qingming Festival",
            "artist": "Zhang Zeduan",
            "source_name": "The Palace Museum",
            "source_url": "https://www.dpm.org.cn/collection/paint/228226.html",
        }
    ],
    "artist_biography_query": [
        {
            "artist": "Zhang Zeduan",
            "biography": "Zhang Zeduan (c.1085-1145), courtesy name Zhengdao, was a famous painter of the Northern Song dynasty. His masterpiece 'Along the River During the Qingming Festival' is a treasure of Chinese painting.",
            "source_name": "The Palace Museum",
            "source_url": "https://www.dpm.org.cn",
        }
    ],
    "dynasty_representative_query": [
        {
            "dynasty": "Tang Dynasty",
            "artifacts": ["Tang Sancai Camel Carrying Musicians", "Yan Zhenqing's Draft of a Eulogy", "Yan Liben's Imperial Carriage"],
            "source_name": "China Overseas Lost Cultural Relics KG",
            "source_url": "https://se-cs2305.yazs.top/docs",
        }
    ],
    "museum_count_query": [
        {
            "museum": "The Metropolitan Museum of Art",
            "artifact_count": 1240,
            "source_name": "The Metropolitan Museum of Art",
            "source_url": "https://www.metmuseum.org/art/collection",
        }
    ],
    "recommended_artifacts_query": [
        {
            "artifact": "Tea Bowl and Dish",
            "recommendations": ["Longquan Celadon Vase", "Jun Ware Bowl", "Ding Ware Plate"],
            "source_name": "Art Institute of Chicago",
            "source_url": "https://www.artic.edu/collection",
        }
    ],
    "same_artist_works_query": [
        {
            "artist": "Zhang Zeduan",
            "works": ["Along the River During the Qingming Festival", "Spring Festival on the River", "Dragon Boat Race"],
            "source_name": "The Palace Museum",
            "source_url": "https://www.dpm.org.cn",
        }
    ],
    "multi_hop_query": [
        {
            "artifact": "Admonitions Scroll",
            "path_nodes": ["Admonitions Scroll", "Zhang Hu", "Yuan Dynasty Collection", "Qianlong Emperor", "The British Museum"],
            "path_relations": ["CREATED_BY", "COLLECTED_BY", "TRANSFERRED_TO", "COLLECTED_BY"],
            "explanation": "《女史箴图》由顾恺之创作，历经张华题跋、元代宫廷收藏、乾隆皇帝珍藏，最终流失至大英博物馆。",
            "source_name": "The British Museum",
            "source_url": "https://www.britishmuseum.org/collection",
        }
    ],
    "compare_artifacts_query": [
        {
            "artifact1": "Admonitions Scroll",
            "artifact2": "Along the River During the Qingming Festival",
            "dynasty1": "Eastern Jin",
            "dynasty2": "Northern Song",
            "material1": "Silk",
            "material2": "Silk",
            "museum1": "The British Museum",
            "museum2": "The Palace Museum",
            "dimensions1": "24.8cm × 348.2cm",
            "dimensions2": "24.8cm × 528.7cm",
            "source_name": "Cultural Heritage KG",
            "source_url": "https://se-cs2305.yazs.top/docs",
        }
    ],
    "artifact_statistics_query": [
        {
            "dynasty": "Tang Dynasty",
            "total_artifacts": 156,
            "types": ["Ceramic", "Painting", "Sculpture", "Calligraphy", "Bronze"],
            "materials": ["Ceramic", "Silk", "Bronze", "Stone", "Paper"],
            "museums": ["The British Museum", "The Metropolitan Museum of Art", "Tokyo National Museum", "Louvre Museum"],
            "source_name": "China Overseas Lost Cultural Relics KG",
            "source_url": "https://se-cs2305.yazs.top/docs",
        }
    ],
    "path_query": [
        {
            "artifact": "Admonitions Scroll",
            "path_nodes": ["Admonitions Scroll", "Tang Dynasty Palace", "Qianlong Emperor", "Yuanmingyuan", "The British Museum"],
            "path_relations": ["COLLECTED_BY", "COLLECTED_BY", "STORED_AT", "COLLECTED_BY"],
            "node_types": ["Artifact", "Dynasty", "Artist", "Museum", "Museum"],
            "explanation": "《女史箴图》原藏于唐代宫廷，后经乾隆皇帝收藏，曾存放于圆明园，1860年流失至大英博物馆。",
            "source_name": "The British Museum",
            "source_url": "https://www.britishmuseum.org/collection",
        }
    ],
}
