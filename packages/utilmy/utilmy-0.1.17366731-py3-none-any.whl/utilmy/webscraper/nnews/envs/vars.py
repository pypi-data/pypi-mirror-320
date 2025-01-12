

apikey1 = os.environ.get("apikey", "")



params1 =  { 'api_key': apikey1,
            'url': '', 
            'wait': '800',
            'premium_proxy': 'false',
            'stealth_proxy': 'false', 
            'country_code':'jp',
             'render_js': 'false'
        }

params2 =  { 'api_key': apikey1,
            'url': '', 
            'wait': '1000',
            'premium_proxy': 'true',
            'stealth_proxy': 'true', 
            'country_code':'jp',
            'render_js': 'true' 
        }



params1b =  { 'api_key': apikey1,
            'url': '', 
            'wait': '500',
            'premium_proxy': 'false',
            'stealth_proxy': 'false', 
            'country_code':'jp',
            'custom_google': 'True'
        }



        