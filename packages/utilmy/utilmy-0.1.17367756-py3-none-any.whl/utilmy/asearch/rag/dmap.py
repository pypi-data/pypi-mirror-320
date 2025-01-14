




activity_tags_ref = """
partnership
funding
m and a
industry news
new product
product
service launch
earnings
listing
expansion
management
approval
regulation 
"""




###3 reduce the size of those keywords
#### ---When using fuzzy --> use this reference.
industry_tags_ref = """
additive manufacturing
ai drug
aircraft
alternative energy
auto
automated store
beauty
bio materials
biometric
biotech
blockchain
business expense
carbon
cell cultured
cell gene
climate
clinical trial
cloude
cloud optimization
fitness
conservation
crm
cyber insurance
cybersecurity
dairy egg
data infrastructure
e commerce
decentralized finance
devops
digital privacy
digital retail    
digital twin
digital wellness
edge computing
edtech
esport
ev economy
extended reality
facial recognition
farming
fertility
financial wellness
fintech
insurance
food delivery
food waste
foundation models
gene therapy
generative ai
health
human gene
hydrogen
identity access
insurtech
last mile
livestock biotech
logistics
longevity
code
machine learning
marketing automation
metaverse
natural fertilizers
banks
online freelancing
pay later
pet
meat
precision medicine                                                                                            
prefab
quantum computing
remote work
residential
restaurant robotics
retail robots
retail trading
sales engagement
satellite
serverless computing
smart factory
smart farming
smart mobility
smart packaging
space travel
supply chain
travel
truck
web
workflow automation
"""

industry_tags_ref = {
"indus_refs": [
    "additive manufacturing",
    "ai drug",
    "aircraft",
    "alternative energy",
    "auto",
    "automated store",
    "beauty",
    "bio materials",
    "biometric",
    "biotech",
    "blockchain",
    "business expense",
    "carbon",
    "cell cultured",
    "cell gene",
    "climate",
    "clinical trial",
    "cloude",
    "cloud optimization",
    "fitness",
    "conservation",
    "crm",
    "cyber insurance",
    "cybersecurity",
    "dairy egg",
    "data infrastructure",
    "decentralized finance",
    "devops",
    "digital privacy",
    "digital retail",
    "digital twin",
    "digital wellness",
    "edge computing",
    "edtech",
    "esport",
    "ev economy",
    "extended reality",
    "facial recognition",
    "farming",
    "fertility",
    "financial wellness",
    "fintech",
    "food delivery",
    "food waste",
    "foundation models",
    "gene therapy",
    "generative ai",
    "health",
    "human gene",
    "hydrogen",
    "identity access",
    "insurtech",
    "last mile",
    "livestock biotech",
    "logistics",
    "longevity",
    "code",
    "machine learning",
    "marketing automation",
    "metaverse",
    "natural fertilizers",
    "banks",
    "online freelancing",
    "pay later",
    "pet",
    "meat",
    "precision medicine",
    "prefab",
    "quantum computing",
    "remote work",
    "residential",
    "restaurant robotics",
    "retail robots",
    "retail trading",
    "sales engagement",
    "satellite",
    "serverless computing",
    "smart factory",
    "smart farming",
    "smart mobility",
    "smart packaging",
    "space travel",
    "supply chain",
    "travel",
    "truck",
    "web",
    "workflow automation"
]
}

def pd_generate_tags(drin: str, coltag="L_cat",  dirout: str="ztmp/", cutoff: int = 95) -> None:
        from utilmy import pd_read_file, pd_to_file
        from rapidfuzz import process, fuzz
        import re
        """
            Generate tags
    
    

        """
        if isinstance(drin, pd.DataFrame):
            df_raw = drin  
        else:    
            df_raw = pd_read_file(drin)

        df_raw['w'] = df_raw[coltag].apply(lambda x: [xi for xi in x.strip().split(" ") if len(xi) > 1])  
        df1 = df_raw['w'].explode()

        df1 = df1.value_counts().reset_index()

        #df2 = df1[ df1['count'].apply(lambda x: x < 20000 and x > 100 )  ]
        df2 = df1[ df1['count'].apply(lambda x:  x > 1 )  ]

        df2 = df2[ df2['w'].apply(lambda x : len(x) >= 3 )]

        df2['w'] = df2['w'].apply(lambda x : x[:-1].lower() if x.endswith("s") else x.lower() )
        
        df2['w'] = df2['w'].apply(lambda x: re.sub(r"[()\',]", "", x))

        df2 = df2[ df2['w'].apply(lambda x : len(x) >= 3 )]
        df2['w'] = df2['w'].apply(lambda x : x[:-1].lower() if x.endswith(("s", "d")) else x.lower() )

        df3 = df2.groupby(['w']).agg({"count": 'sum'}).reset_index().sort_values('count', ascending=[False])
        log(df3)
        pd_to_file(df3, dirout + "/new_tags.csv", show=1, sep="\t", index=False)



def pd_clean_industry_tags(drin: str,  drout: str, cutoff: int = 95) -> None:
    from utilmy import json_load, pd_read_file, pd_to_file
    from rapidfuzz import process, fuzz
    import pandas as pd
    
    # Load DataFrame
    df = pd_read_file(drin)

    tag_all = []

    for i1, x in df.iterrows():
        question = x[question]
        xtags = str(x[indus_tags]).strip().split(",")
        xtags = [tag.strip() for tag in xtags if tag.strip()]
        tag_all.extend([(question, xi) for xi in xtags])

    df2_raw = pd.DataFrame(tag_all, columns=[question, tag])

    df2 = df2_raw.drop_duplicates([tag])
    df2 = df2.sort_values(tag, ascending=True)

    tag_ref = [xi.strip() for xi in industry_tags_ref["indus_refs"] if len(xi.strip()) > 1]

    def norm_tag(x):
        try:
            matches = process.extract(x.strip(), tag_ref, scorer=fuzz.partial_ratio, score_cutoff=cutoff)
            best_matches = [match[0] for match in matches if match[1] >= cutoff]
            return ";".join(best_matches) if best_matches else ""
        except Exception as e:
            print(f"Error: {e}")
            return 
        
    df2[tag2] = df2[tag].apply(lambda x: norm_tag(x))

    df2_ = df2_raw.merge(df2[[tag, tag2]], on=tag, how=left)
    df2_ = df2_.groupby(question).agg({
               tag:  lambda x: ",".join(x.unique()),  
               tag2: lambda x: ",".join(x.unique())
    }).reset_index()

    # Save the final dataframae
    pd_to_file(df2_, f{drout}/df_industry_tag_normed.parquet)




