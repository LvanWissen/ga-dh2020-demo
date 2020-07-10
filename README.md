# ga-dh2020-demo
Golden Agents DH2020 demo

Images are served through Image API level 0 (static) and are therefore shrunk to 75% quality. The full archive can be browsed at https://archief.amsterdam/5075/2408.

## Data

### Queries

`canvasmetadata`

For getting the metadata from the index records

```SPARQL
PREFIX pnv: <https://w3id.org/pnv#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX saa: <https://data.goldenagents.org/datasets/SAA/ontology/>

SELECT * WHERE {

  ?deed saa:actType ?actType ;
        saa:registrationDate ?registrationDate ;
        saa:identifier ?identifier ;
        saa:description ?description ;
        saa:language ?language ;
        saa:mentionsNotary/pnv:hasName/pnv:literalName ?notary ;
        saa:inventoryNumber "2408" ;
        saa:urlScan ?scan .
  
  OPTIONAL { ?deed saa:mentionsRegisteredName/pnv:literalName ?person . }
  OPTIONAL { ?deed saa:mentionsLocation/rdfs:label ?location . }
  
  BIND(CONCAT(STRAFTER(STR(?scan), 'Scan/'), '.jpg') AS ?image)
  
} LIMIT 100000
```

For getting the types (persons/locations) from the index records
```SPARQL
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX as: <http://www.w3.org/ns/activitystreams#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX schema: <http://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ga: <https://data.goldenagents.org/ontology/>
PREFIX saa: <https://data.goldenagents.org/datasets/SAA/ontology/> 
PREFIX pnv: <https://w3id.org/pnv#>

SELECT DISTINCT ?image ?type ?label ?coords WHERE {

  ?inventorySAA saa:inventoryNumber "2408" .
  
  ?inventorySAA saa:hasParts/saa:hasDigitalRepresentation/foaf:depiction ?url .
  
  ?indexRecord saa:urlScan ?scan .
  ?scan saa:url ?url .
  
  BIND(CONCAT(STRAFTER(STR(?url), '#'),'.jpg') AS ?image) .
  
  ?annotation oa:hasTarget [ oa:hasSource ?scan ;
                             oa:hasSelector/rdf:value ?coords ] ;
              ^prov:wasDerivedFrom [ a ?type] ;
              oa:hasBody/rdfs:label ?label .

} ORDER BY ?image
```