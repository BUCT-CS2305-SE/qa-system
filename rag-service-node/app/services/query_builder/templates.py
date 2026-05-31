QUERY_TEMPLATES = {
    "artifact_museum_query": "MATCH (a:Artifact {name:$artifact_name})-[:COLLECTED_BY]->(m:Museum) RETURN a.name AS artifact, m.name AS museum, m.detail_url AS source_url",
    "artifact_period_query": "MATCH (a:Artifact {name:$artifact_name})-[:BELONGS_TO_DYNASTY]->(d:Dynasty) RETURN a.name AS artifact, d.name AS dynasty",
    "artifact_material_query": "MATCH (a:Artifact {name:$artifact_name})-[:MADE_OF]->(m:Material) RETURN a.name AS artifact, m.name AS material",
    "artifact_type_query": "MATCH (a:Artifact {name:$artifact_name})-[:HAS_TYPE]->(t:Type) RETURN a.name AS artifact, t.name AS type",
    "artifact_description_query": "MATCH (a:Artifact {name:$artifact_name}) RETURN a.name AS artifact, a.description AS description",
    "artifact_dimensions_query": "MATCH (a:Artifact {name:$artifact_name}) RETURN a.name AS artifact, a.dimensions AS dimensions",
    "painting_author_query": "MATCH (a:Artifact {name:$artifact_name})-[:CREATED_BY]->(p:Artist) RETURN a.name AS artifact, p.name AS artist",
    "artist_biography_query": "MATCH (p:Artist {name:$artist_name}) RETURN p.name AS artist, p.biography AS biography",
    "dynasty_representative_query": "MATCH (d:Dynasty {name:$dynasty_name})<-[:BELONGS_TO_DYNASTY]-(a:Artifact) RETURN d.name AS dynasty, collect(a.name) AS artifacts LIMIT 10",
    "museum_count_query": "MATCH (m:Museum {name:$museum_name})<-[:COLLECTED_BY]-(a:Artifact) RETURN m.name AS museum, count(a) AS artifact_count",
    "recommended_artifacts_query": "MATCH (a:Artifact {name:$artifact_name}) RETURN a.name AS artifact",
    "same_artist_works_query": "MATCH (a:Artifact)-[:CREATED_BY]->(p:Artist {name:$artist_name}) RETURN collect(a.name) AS works, p.name AS artist",
}