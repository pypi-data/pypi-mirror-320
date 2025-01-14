"""
    Summary:
          Summary of each news article. + reference URL


    Eval of the summary ??
    Idea : Reverse  Queston:

      News Articles  : Merged manually 5 of them (Thruth).
           ---> Ask LLM to generate precise questions. ---> list of questions (store on disk).



          Use those questions --> Sumarizer ---> LLM summary (to evaluate)


          Ask LLM to compare the summary with reference text (that we know as reference).
             to find differences, innacurate facts.


          Pypi /  github: new cross check.
          Integer: 1 to 10,


       Step 1: think about pipelines as empty functions.

       1 row : 1 eval:
           df['text1', 'text2', 'text3', 'merge_text', 'question_list_from_llmn', ],



    Eval pipeline for Summarizer

       Check if summary is "correct"








"""