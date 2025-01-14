if "######## import":
    import sys, json, os, warnings, random, string
    warnings.filterwarnings("ignore")
    from box import Box
    import pandas as pd, numpy as np
    from pydantic import BaseModel, Field
    from typing import List, Dict, Union, Tuple
    from copy import deepcopy
    from functools import lru_cache

    from utilmy import log, log2, pd_read_file, pd_to_file, json_save, date_now
    from utilmy import diskcache_load, diskcache_decorator
    from utilmy import json_load
    from utils.util_text import str_fuzzy_match_is_same, date_get



from rag.rag_summ2 import search_run





#########################################################################################
def testq(name="q1", maxq=1, maxkey=1, full="0"):
    """

         python tests.py  testq  --name q1_ok  --maxq 1  --maxkey 1


    """
    dirout0 = "ztmp/arag/tests/query/"
    os.environ['DEBUG_query' ] ="0"


    from utilmy import config_load
    #qlist = config_load("tests/questions.yaml")
    # log("qlist: ", str(qlist)[:100])

    #qlist =  qlist0 | qlist
    qlist = qlist0


    qused = qlist[name]
    qused = [xi.strip() for xi in qused.split("\n") if len(xi.strip() ) > 2  ]
    qused = np_unique(qused)
    log(qused[:20])
    log('Nquestions:', len(qused))


    keyname = 'industry'
    keylist = KEYW[keyname].split("\n")
    keylist = [xi for xi in keylist if len(xi) >2]

    log("########### Start questions ########################################")
    done = set()
    res  = []
    y, m, d, h, ts = date_get()
    diroutk = dirout0 + f"/year={y}/month={m}/day={d}"

    for ii, qi in enumerate(qused[:maxq]):
        log("---- ", ii, qi)
        qi = qi.split("#")[-1]

        for key in keylist[:maxkey]:
            qi = qi.replace('{' + keyname + '}', key)

            if qi in done: continue

            try:
                dd = search_run(query=qi, meta=None)
                res.append([name, qi, json.dumps(dd)])
                done.add(qi)
            except Exception as e:
                log(e)

        if ii % 20 == 0:
            res = pd.DataFrame(res, columns=['type', 'query', 'answer'])
            pd_to_file(res, diroutk + f"/qparse_{ts}_{ii}_{len(res)}.parquet", show=1)
            res = []

    if len(res) > 0:
        res = pd.DataFrame(res, columns=['type', 'query', 'answer'])
        pd_to_file(res, diroutk + f"/qparse_{ts}_{ii}_{len(res)}.parquet", show=1)



def key_replace(qi, keylist):
    import re
    keys = re.findall(r'<(.*?)>', qi)

    for ki in keys:
        qi =qi.replace(ki, )





if "############ question ###################################################":
    qlist0 = {'q1_indus': """   What the impact of US elected president Donald trump in {industry}  ?"

                           Provide a list of industries for <com_name> ?
                           
                Explain the business model of  companies in <industry> industry
            
                Provide a list of leading <industry2> companies from US
            
                Provide some summary on regulation in <industry> industry
            
                Provide some competitors analysis in <industry> industry
            
                Who are the key players in the <industry> industry ?
                        
                Highest funded startup in the <industry> industry
            
                Have companies developed any GenAI solutions in smart factory?
            
                Which company develops CAR-T therapies ?                           

                     """,

              "q2_notok": """

                       List down Siemens' partnerships with Microsoft
                       

              """


       ,"not_good": """
       

            Remove common words: from search.
            from context.
                 
        Bad retrieval:
           Provide list of startup in nuclear fusion industry and the technical technologies used for each company.
              
       
       """

        ,"comments" : """
        
              
           
           
            Remove common words: from search.
                from context.
                 
                
        
           Best Funding is not so good....
        
           Need to pick from the funding list sorting...
          
          
          What are the emerging trends in the sustainable packaging space? : General industry Qs

            Who are the top 10 early stage startups in the autonomous ai agents space and what’s their funding? : Company list
            
            Who are Hydrosat’s competitors?: 
            
            Compare Quantinuum and Rigetti Computing on funding and other important product metrics : Comparison
            
            
            What’s the market size breakdown for generative ai applications ? Provide a visualization. : Visual
            
            
            
            What are the larger incumbents doing in the AI Data Centre space ? 
            
            Who have they invested in ? 
             
             :Out of coverage but hot topic





For Edge AI on Minaz question


           What are the emerging trends in the sustainable packaging space ? 

           Provide list of startup companies and their funding in AI Agent industry

           List of competitors of Hydrosat company  

           Compare Quantinuum company and Rigetti Computing company on funding and other important metrics

           Provide details on Quantinuum company

           Provide breakdown of market size of generative ai application industry

           What are the activities of biggest companies or incumbents in the AI Data Center industry ? 

           Provide a market map for Multi-turn text generation, Single-turn text generation 
                    and Image generation ?





        Provide a market map of companies for multi-turn text generation industry


  Construct


          New question from Minaz 

               : General industry Qs


                What are the emerging trends in the sustainable packaging space ? 


                What are the top 10 early stage startups in the AI agent space ?


                Who are the top 10 early stage startups in the autonomous AI agents space ?



                ### Goo questions
                Provide list of startup companies and their funding in AI Agent industry

                Provide investments in AI agent industry  

                 what’s their funding? 
                 Does not work:  


                 : Company list

                Who are Hydrosat’s competitors ?   



                   List of Edge is shorter but more relevant than 


                ####  : Comparison

                     Compare Quantinuum and Rigetti Computing on funding and other important product metrics.


                ##### 

                   What’s the market size breakdown for generative ai applications. 

                  Provide a visualization. 


                : Visual : XX Cannot 


                What are the larger incumbents doing in the AI Data Centre space ? 

                Who have they invested in? 

                 :Out of coverage but hot topic


                #####

                    Construct a market map for Multi-turn text generation, Single-turn text generation 
                    and Image generation ?



                    Provide a list of companies for multi-turn text generation industry


                What are the emerging trends in the sustainable packaging space? : General industry Qs
                Who are the top 10 early stage startups in the autonomous ai agents space and what’s their funding? : Company list
                Who are Hydrosat’s competitors?:  Comparison
                Compare Quantinuum and Rigetti Computing on funding and other important product metrics : Comparison
                What’s the market size breakdown for generative ai applications. Provide a visualization. : Visual
                What are the larger incumbents doing in the AI Data Centre space? Who have they invested in?  :Out of coverage but hot topic
                



              Provide some description on AI Agent market growth ? 


              What are the recent partnerships in Microsoft in 2024 ?

              

              Provide market size of Truck industry 

              What are the driving demands of AI Agent industry ?

              Provide some summary on regulation in AR VR industry

              List of investments in digital twins industry.

              Provide a list of food tech companies from Israel .

              Provide some details on steakholder foods company

              What is the market size of food tech industry ?



            Provide some market size of Truck industry.
            
            
            
            Provide some summary on regulation in renewable energy industry.
            
            List down investments made by Nvidia in Generative AI Applications industry
            
            List investments in openai
            
            lsit investment by openai
            
            What is the current status of quantum battery industry ?
            
            lsit donwn investment in carbon industry.
            
            What is the impact of new president donald trump on auto tech industry ?
            
            
            
            How much total funding did startups in the Extended Reality (XR) industry raise in Q2 2024 ?
            
            Explain the business model of companies in Food Waste industry
            
            Who are the key players in the Generative AI infrastructure industry ?
            
            List down indutries for Bosch
            
            List down strategies in Siemens .
            
            Provide some competitors analysis in VR AR industry
            
            Who are the key players in the Generative AI infrastructure industry ?
            
            List down investments made by Nvidia in Generative AI Applications industry
            
            Highest funded startup in the Web3 industry
            
            Have companies developed any GenAI solutions in smart factory ?
            
            Which company develops CAR-T therapies ?
            
            Which companies in Carbon industry ?
            
            List down strategies in Siemens
            
            Provide activities by Alphabet in the data infrastructure ?
            
            Provide some insights on sustainability
            
            Explain the drivers for Web3 industry
            
            What are the partnerships of Microsoft in Generative AI in 2024?
            
            What are some case studies on banks monetizing their underutilized assets ?
            
            What is the addressable market for additive Manufacturing
            
            have companies developed any GenAI solutions in smart factory?
            
            What are companies offering GPUaaS solutions ?
            
            What companies provide solutions for AI servers ?
            
            What is the total addressable market for human gene editing in the US?
            
            Which companies specialize specifically in the production of virtual reality (VR) headsets ?
            
            What is the market size for human gene editing for sickle cell disease?
            
            Provide some functional nutrition companies that offer apps that provide personalized solutions
            
            What are the leading companies offering AR surgical guidance solutions ?
            
            What are the partnerships of Siemens for Digital Twins ?
            
            Give me a list of Embodied AI companies ?
            
            Market size of cybersecurity industry ?
            
            Market size of renewable energy ?
            
            Provide some details on Nutrition industry.
            
            List of companies in Nutrition industry.
            
            What are the partnerships of Siemens for Digital Twins ?
            
            What are the recent activities of carbon capture industry ?
            
            Which companies in Carbon industry ?
            
            What neobanks have launched GenAI solutions ?
            
            List of investment in Renewable industry ?
            
            List of investors in OpenAI ?
            
            Give me investments by Amazon.
            
            List of investments in Amazon.
            
            List of investments by Microsoft in Generative AI ?
            
            What is the impact of new elected US president Donald Trump in Cyber security ?
            
            What is the impact of stringent emissions regulations on the Carbon Capture market?
            
            What are the partnerships of Microsoft in Generative ai 2024 ?
            
            What are the acquisitions in renewable in 2023 ?
            
            What are the activities of Mastercard in 2024 ?
            
            What is the CAGR in renewable energy in 2024 ?
            
            Summarize the activities of Toyota in 2024 ?
            
            Compare partnerships between Siemens and Hitachi in 2024 ?
            
            Market size of cybersecurity industry ?
            
            What are the partnerships of Microsoft in Generative AI in 2024 ?
            
            Provide a list of companies in genrative ai industry
            
            Describe Carbon industry.
            
            Find Mistral company
            
            Give some definition of quantum battery
            
            Describe EV Industry
            
            Provide some details on Nutrition industry.
            
            Find anthropic company
            
            What are the recent activities of carbon capture industry ?
            
            Provide a definition of quantum battery technoloogy ?
        
        """


        , "q1_ok": """

                Explain the business model of  companies in Food Waste industry
            
                Provide a list of leading food tech companies from Israel
            
                Provide some summary on regulation in renewable energy industry
            
                Provide some competitors analysis in VR AR industry
            
                Who are the key players in the Generative AI infrastructure industry ?
            
                List down investments made by Nvidia in Generative AI Applications industry
            
                Highest funded startup in the Web3 industry
            
                Have companies developed any GenAI solutions in smart factory?
            
                Which company develops CAR-T therapies ?
            
                Which companies in Carbon industry ?
            
                Give me a list of Embodied AI companies ?
            
                List down investments made by Nvidia in Generative AI Applications industry
            
                What are the leading companies offering AR surgical guidance solutions ?
            
                How much total funding did startups in the Extended Reality (XR) industry raise in Q2 2024?
            
                Who are the key players in the Generative AI infrastructure industry ?
            
                List down strategies in Siemens' strategy section
            
                What neobanks have launched GenAI solutions ?
            
                List down strategies in Siemens
            
                Any activity by Alphabet in the data infrastructure ?
            
                Provide some insights on sustainability
            
                Explain the drivers for Web3 industry
            
            
                How much total funding did startups in the Extended Reality (XR) industry raise in Q2 2024 ?
            
                What are the partnerships of project44 in Supply chain in 2024 ?
            
            
                What are some case studies on banks monetizing their underutilized assets ?
            
            
                What is the addressable market for additive Manufacturing
            
            
                have companies developed any GenAI solutions in smart factory?
            
            
               What are companies offering GPUaaS solutions ?   ### Ok good
            
               What companies provide solutions for AI servers ?
            
            
               What is the total addressable market for human gene editing in the US?
            
               Which companies specialize specifically in the production of virtual reality (VR) headsets ?
            
               What is the market size for human gene editing for sickle cell disease?
            
               Provide some functional nutrition companies that offer apps that provide personalized solutions
            
               What are the leading companies offering AR surgical guidance solutions ?
            
               What are the partnerships of Siemens for Digital Twins ?
            
            
               Market size of cybersecurity industry ?
            
               Market size of renewable energy ?
            
               Provide some details on Nutrition industry.
            
               List of companies in Nutrition industry.
            
               What are the partnerships of Siemens for Digital Twins ?
            
               What are the recent activities of carbon capture industry ?
        
        

            """

              }



if "############ Utils ###################################################":

    def np_unique(ll):
        ll2 = []
        for xi in ll:
            if xi not in ll2:
                ll2.append(xi)
        return ll2

    def str_replace_punctuation(text, val=" "):
        import re
        return re.sub(r'[^\w\s]', val, text)


    def str_split_right_first(s: str, charlist=None) -> tuple:
        charlist = [ "|", "-" ] if charlist is None else charlist
        imax= -1
        s = str(s)
        for ci in charlist:
            ix = s.rfind(ci)
            if ix != -1:
                imax = max(imax, ix)

        if -1 < imax < len(s) :
            log(imax)
            return s[:imax], s[imax + len(ci):]

        return s, ""


    def str_split_right_last(s: str, charlist=None) -> tuple:
        charlist = [ "|", "-" ] if charlist is None else charlist
        imin= 999999999
        s = str(s)
        for ci in charlist:
            ix = s.rfind(ci)
            if ix != -1:
                imin = min(imin, ix)

        if -1 < imin < len(s) :
            log(imin)
            return s[:imin], s[imin + len(ci):]

        return s, ""


    def str_contain_fuzzy_list(word, wlist, threshold=80):
        """
        Check if word fuzzy matches any string in wlist using rapidfuzz
        """
        from rapidfuzz import fuzz
        w0 = str(word.lower())
        return any(fuzz.partial_ratio(w0, w.lower()) >= threshold for w in wlist)


    def str_contain_fuzzy_wsplit(word, sentence, sep=" ", threshold=80):
        """
        Check if word fuzzy matches any string in wlist using rapidfuzz
        """
        from rapidfuzz import fuzz
        w0 = str(word.lower())
        wlist = str(sentence).lower().split(sep)
        return any(fuzz.partial_ratio(w0, w.lower()) >= threshold for w in wlist)


    def str_match_fuzzy(word, word2="", sep=" ", threshold=80):
        """
        Check if word fuzzy matches any string in wlist using rapidfuzz
        """
        from rapidfuzz import fuzz
        w0 = str(word.lower())
        w2 = str(word2).lower()
        return fuzz.partial_ratio(w0, w2) >= threshold


    def json_save2(llg, dirout):
        y,m,d,h = date_now(fmt="%Y-%m-%d-%H").split("-")
        ts      = date_now(fmt="%y%m%d_%H%M%s")
        json_save(llg.to_dict(), dirout + f"/year={y}/month={m}/day={d}/hour={h}/chat_{ts}.json" )


    def str_norm(text):
        return str(text).lower().translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))


    def str_find(x:str,x2:str, istart=0):
        try:
            i1 = x.find(x2, istart)
            return i1
        except Exception as e:
            return -1


    def str_docontain(words, x):
        x2 = str(x).lower()
        for wi in words.split(" "):
            if wi.lower() not in x2 : return False
        return True


    def str_fuzzy_match_list(xstr:str, xlist:list, cutoff=70.0):
        from rapidfuzz import process, fuzz
        results = process.extract(xstr, xlist, scorer=fuzz.ratio, score_cutoff=cutoff)
        return [result[0] for result in results]


    def str_fuzzy_match(str1, str2, threshold=95):
        from rapidfuzz import fuzz
        score = fuzz.ratio( str(str1).lower(), str(str2).lower() )
        if score >= threshold : return True
        return False


    def do_exists(var_name):
        return var_name in locals() or var_name in globals()


    def to_int(x, val=-1):
        try:
            return int(x)
        except Exception as e:
            return val




KEYW = Box({})
KEYW.industry= """
    Generative AI Applications
    Generative AI Infrastructure
    Current-gen renewables
    Smart Factory
    Alternative Energy
    Additive Manufacturing
    Digital Twin
    Next-gen Cybersecurity
    Supply Chain Tech
    Foundation Models
    Carbon Capture
    AI Drug Discovery
    Hydrogen Economy
    B2B SaaS Management Platforms
    Age Tech
    Remote Work Tools
    Bio-based Materials
    Humanoid Robots
    Financial Wellness Tools
    Neobanks
    Longevity Tech
    Remote Work Infrastructure
    InsurTech: Personal Lines
    Data Infrastructure & Analytics
    EV Economy
    Retail Industry Robots
    Preventive Healthcare
    Auto Tech
    Identity & Access Management
    Smart Building Technology
    Climate Risk Analytics
    Carbon Management Software
    Quantum Computing
    Workflow Automation Platforms
    Edge Computing
    Oil & Gas Tech
    Vertical Farming
    Next-gen Satellites
    Last-mile Delivery Automation
    Logistics Tech
    Waste Recovery & Management Tech
    FinTech Infrastructure
    Space Travel and Exploration Tech
    Precision Medicine
    InsurTech: Commercial Lines
    Sustainable Aquaculture
    Customer Service Platforms
    Energy Optimization & Management Software
    Digital Wellness
    Threat Prevention Toolchain
    Smart Farming
    Passenger eVTOL Aircraft
    Military Tech
    Smell Tech
    Sales Engagement Platforms
    Extended Reality
    Crop Biotech
    Metaverse Platforms
    Natural Language Processing Tools
    HR Tech
    Content Creation Tools
    Automated Stores
    Buy Now, Pay Later
    Hospital-at-Home
    Mental Health Tech
    EdTech: K-12
    Capital Markets Tech
    Decentralized Finance (DeFi)
    Conservation Tech
    Beauty Tech
    Cell & Gene Therapy
    Cloud-native Tech
    Truck Industry Tech
    Digital Privacy Tools
    Telehealth
    Alternative Ingredients
    DevOps Toolchain
    Next-gen Medical Devices
    Natural Fertilizers
    Next-gen Displays
    Retail Trading Infrastructure
    Psychedelic Medicine
    Ecommerce Platforms
    Digital Humans
    EdTech: Corporate Learning
    Hospital Management
    Mining Tech
    Regenerative Agriculture Platforms
    Commercial PropTech
    Higher EdTech
    Health Benefits Platforms
    Smart Security Tech
    Functional Nutrition
    Serverless Computing
    Biopesticides
    P2P Financial Platforms
    Next-gen Semiconductors
    Next-gen Email Security
    Clinical Trial Technology
    InsurTech: Infrastructure
    SME CRM
    Digital Retail Enhancement Platforms
    Cold Chain Innovation
    Contract Management Tools
    Plant-based Dairy & Egg
    Healthcare Resourcing Platforms
    Cloud Optimization Tools
    Wearable Tech
    Facial Recognition
    Human Gene Editing
    Travel Tech
    Smart Homes: Energy & Water Solutions
    Marketing Automation
    Residential PropTech
    Neurostimulation Tech
    Plant-based Meat
    Hygiene Tech
    Biometric Payments
    Cell-cultured Meat
    Alternative Data
    Cyber Insurance
    Enterprise Blockchain Solutions
    Clinical Decision Support Systems
    Smart Packaging Tech
    Commercial Drone Tech
    Neuromorphic Computing
    Low-code Platforms
    Creator Economy
    Shipping Tech
    Convenience Foods
    Cannabis
    Online Freelancing Platforms
    Machine Learning Infrastructure
    Next-gen Private Mobile Networks
    Online Food Delivery
    Connected Fitness
    Sustainable Finance
    Hospital Interoperability
    Bioprinting
    Business Expense Management
    Prefab Tech
    Alternative Living
    Restaurant Industry Robotics
    Sports Tech
    Web3 Ecosystem
    Infectious Disease Tech
    Functional Ingredients
    Cloud Kitchens
    No-code Software
    Legal Tech
    Brain-computer Interfaces
    Pollution Management Tech
    Fertility Tech
    Large-molecule Therapeutics
    Smart Mobility Information
    Furniture Tech
    Animal Therapeutics
    Food Waste
    Digital Wallets
    Shared Mobility
    Esports
    Pet Care Tech
    Livestock Biotech
    Initial
    Biosimilars
    Construction Tech
    Tissue Targeting Therapeutics
    Automated Content Moderation
    Custom hub mock: Consumer lending
    Custom Hub Mock: The Mills Fabrica
    NFT
    Smart Packaging
    Next-gen Environmental Services
    Media Tech
    Social Commerce
    Cryptocurrencies
    Radiopharmaceuticals
    RNA Therapeutics
"""




########################################################################################
if __name__ == '__main__':
    import fire
    fire.Fire()
