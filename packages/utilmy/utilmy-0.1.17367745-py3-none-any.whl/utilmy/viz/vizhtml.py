# -*- coding: utf-8 -*-
""" Converter python Graph ---> HTML page
Docs::


    https://colab.research.google.com/drive/1NYQZrfAPqbuLCt9yhVROLMRJM-RrFYWr#scrollTo=Rrho08zYe6Gj
    https://colab.research.google.com/drive/1NYQZrfAPqbuLCt9yhVROLMRJM-RrFYWr#scrollTo=2zMKv6MXOJJu


    pip install python-box python-highcharts  mpld3 pandas-highcharts fire  pretty-html-table matplotlib ipython
    pip install utilmy

    https://try2explore.com/questions/10109123
    https://mpld3.github.io/examples/index.html
    issue: mpld3.fig_to_html throws AttributeError: module 'matplotlib.dates' has no attribute '_SwitchableDateConverter'
    solved by adding matplotlib==3.2.1 mpld3==0.5.5
    https://stackoverflow.com/questions/70132396/mpld3-fig-to-html-throws-attributeerror-module-matplotlib-dates-has-no-attrib
    github isuue link : https://github.com/mpld3/mpld3/issues/504#event-5681391653

    https://notebook.community/johnnycakes79/pyops/dashboard/pandas-highcharts-examples
    https://datatables.net/

    https://www.highcharts.com/docs/getting-started/how-to-set-options


    https://pyviz.org/tools.html
            Name        Stars   Contributors    Downloads       License Docs    PyPI    Conda   Sponsors
            networkx                                        -
            graphviz                                        -
            pydot                           -           -
            pygraphviz                                      -
            python-igraph                                       -
            pyvis                                       -
            pygsp                                       -
            graph-tool              -       -       -       -
            nxviz                                       -
            Py3Plex                 -               -   -
            py2cytoscape                                        -
            ipydagred3                          -           -
            ipycytoscape                            -           -
            webweb                                      -
            netwulf                 -               -   -
            ipysigma                    -       -       -

"""
import os, sys, random, numpy as np, pandas as pd, fire, time
from datetime import datetime
from typing import List
from tqdm import tqdm
from box import Box

from utilmy import log
from utilmy.viz.css import getcss
from utilmy.viz.test_vizhtml import (test1, test2, test3, test4, test_scatter_and_histogram_matplot, test_pd_plot_network, 
  test_page, test_cssname, test_external_css, test_table, test_getdata, test_colimage_table, test_tseries_dateformat, test_plot_network_highcharts, test_plot_parallel_highcharts
)

try :
   pass
   # import matplotlib.pyplot as plt
   # import mpld3
   # from highcharts import Highchart
   # from pyvis import network as net
except :
   #from utilmy.utilmy_base import sys_install
   #sys_install(cmd= cmd)
   log("pip install python-box python-highcharts dateparser matplotlib==3.2.1  pandas-highcharts  pretty-html-table   --upgrade-strategy only-if-needed")
   log("pip install mpld3==0.5.7 pandas-highcharts pyvis  --upgrade-strategy only-if-needed")
   1/0  ### exit Gracefully !

   
   


############################################################################################
#### Test and Example usage ################################################################
def help():
    """  Help function
    """
    suffix = "\n\n\n ##############################\n"
    ss  = "from utilmy.vi.vizhtml import * \n\n"
    ss += "data = test_getdata() \n\n "
    ss += help_get_codesource(test1) + suffix
    ss += help_get_codesource(test2) + suffix
    ss += help_get_codesource(test3) + suffix
    ss += help_get_codesource(test_scatter_and_histogram_matplot) + suffix
    ss += help_get_codesource(test_pd_plot_network) + suffix
    ss += help_get_codesource(test_cssname ) + suffix
    ss += help_get_codesource(test_external_css ) + suffix
    ss += help_get_codesource(test_table ) + suffix
    ss += help_get_codesource(test_colimage_table ) + suffix
    ss += help_get_codesource(test_page ) + suffix
    # ss +=  "Template CSS: \n\n " + str( CSS_TEMPLATE.keys()) + suffix
    ss +=  "colormap_list : \n\n " + str(colormap_get_names()) + suffix
    print(ss)


      
 
      
def test_all():
    """  Test all functions in this module
    """
    from utilmy.viz import vizhtml as vi
    log("Visualization ")
    log(" from utilmy.viz import vizhtml as vi     ")
    test1()
    test2()
    test3()
    test4()
    test_scatter_and_histogram_matplot()
    test_pd_plot_network()
    test_cssname()
    test_external_css()      
    test_table()       
    test_colimage_table()
    test_page()
    test_tseries_dateformat()
    test_plot_network_highcharts()
    test_plot_parallel_highcharts()
   
#####################################################################################
def show(file_csv_parquet:str="myfile.parquet", title='table',format: str='blue_light',dir_out='table.html', css_class=None, use_datatable=True, 
         table_id=None,):
    """  Open HTML file with the parquet file data.
    Docs::

            file_csv_parquet="myfile.parquet":   path to the parquet file
            title='my title':           title of table
            format='blue_light':        format of table
            dir_out="./myexport/":      path to the output file
            css_class=None:             css class of the table
            use_datatable=True   :      Use datable interactive
            table_id=None        :      custom table id in str

    """
    from utilmy import pd_read_file
    df = pd_read_file(file_csv_parquet)
    log(df)
    title = title + "<br>" + file_csv_parquet
    doc = htmlDoc(dir_out="", title=title, format=format, cfg={})
    doc.h1(title) 
    doc.table(df, use_datatable=use_datatable, table_id=table_id, custom_css_class=css_class)
    doc.save(dir_out)
    doc.open_browser()
      
      
def show_table_image(df, colgroup= None, colimage = None,title=None,format: str='blue_light',dir_out='print_table_image.html', 
                     custom_css_class=None, use_datatable=False, table_id=None,):
    """ Show table images
    Docs::

            df="df"              :        dataframe
            colgroup=None        :        column group to show in the table
            colimage=None        :        column image to show in the table
            title=None           :        title of table
            format='blue_light'  :        format of table
            dir_out="./myexport/":        path to the output file
            custom_css_class=None:        css class of the table
            use_datatable=False  :        Use datable interactive
            table_id=None        :        custom table id in str

    """                
    if isinstance(df, str) : ## path
       from utilmy import pd_read_file
       df = pd_read_file(df)

    if colimage:
        colimage = [colimage] if isinstance(colimage, str) else colimage
        for ci in colimage : 
             df[ci] = df[ci].map('<img src="{}" width="50px" height="50px">'.format)

    if colgroup:
        blank_row=[np.nan for i in df.columns]

    l = []
    for n,g in df.groupby(colgroup):
        l.append(g)
        l.append(pd.DataFrame([blank_row], columns=df.columns, index=[0]))

    df = pd.concat(l,ignore_index=True).iloc[:-1]

    doc = htmlDoc(title=title, format='myxxxx',css_name='default', cfg={})
    if title: doc.h1(title) 
    doc.table(df, use_datatable=use_datatable, table_id=table_id, custom_css_class=custom_css_class)
    doc.html = doc.html.replace('&lt;','<')
    doc.html = doc.html.replace('&gt;','>')
    doc.html = doc.html.replace('width: auto"></td>','width: auto">&nbsp;</td>')
    doc.save(dir_out)
    doc.open_browser() 
   
   
   
   
#####################################################################################
#### HTML doc ########################################################################
class htmlDoc(object):
    def __init__(self, dir_out="", mode="", title: str = "", format: str = None, cfg: dict = None,
                 css_name: str = "default", css_file: str = None, jscript_file: str = None,
                 verbose=True, **kw):
        """  Generate HTML page to display graph/Table.
        Combine pages together.
        Docs::

                dir_out="./"      :        Nmae of the output directory.
                title=None        :        Title of the html file.
                cfg={}            :        Graph title and image size in object.
                css_name="default":        Add prebuilt css to html page (default, a4, border, a3d, grey).
                css_file=""       :        path to extenal css file if any.
                jscript_file=""   :        path to extenal css file if any.
                verbose="True"    :        Print log.

        """
        import mpld3

        self.verbose     = verbose
        self.fig_to_html = mpld3.fig_to_html
        cfg          = {} if cfg is None else cfg
        self.cc      = Box(cfg)  # Config dict
        self.dir_out = dir_out.replace("\\", "/")
        self.head    = f"  <html>\n<head>\n"
        self.html    = "\n </head> \n<body>"
        self.tail    = "\n </body>\n</html>"

        ##### HighCharts
        links = """<link href="https://www.highcharts.com/highslide/highslide.css" rel="stylesheet" />
              <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
              <script type="text/javascript" src="https://code.highcharts.com/11/highcharts.js"></script>
              <script type="text/javascript" src="https://code.highcharts.com/11/highcharts-more.js"></script>
              <script type="text/javascript" src="https://code.highcharts.com/11/modules/heatmap.js"></script>
              <script type="text/javascript" src="https://code.highcharts.com/11/modules/histogram-bellcurve.js"></script>
              <script type="text/javascript" src="https://code.highcharts.com/11/modules/exporting.js"></script>
              <script src="https://d3js.org/d3.v4.js"></script>
              <script src="https://d3js.org/d3-hexbin.v0.2.min.js"></script>
              <link href="https://fonts.googleapis.com/css2?family=Arvo&display=swap" rel="stylesheet"> """
        
        links = links + f'\n<link rel="stylesheet" href="{css_file}">' if css_file else links
      
        self.head = self.head + """<title>{title}</title>
              {links}""".format(title=title,links=links)
         
        self.tail = f"\n<script src='{jscript_file}'></script>\n" + self.tail if jscript_file else self.tail

        self.add_css(getcss(css_name))
        # self.add_css(css_get_template(css_name=css_name))

        if css_name=="a4":
          self.html = self.html + '\n <page size="A4">'
          self.tail = "</page> \n" + self.tail

    def tag(self, x):  
        """  Add tage to html
        Docs::

            x      :        Nmae of the output directory.            
        """
        self.html += "\n" + x
    def h1(self,  x,css: str=''): 
        """  Add h1 to html
        Docs::

            x         :        text to place inside html tag.
            css=""    :        css style to h1.
        """
        self.html += "\n" + f"<h1 style='{css}'>{x}</h1>"
    def h2(self,  x,css: str=''): 
        """  Add h2 to html
        Docs::

            x         :        text to place inside html tag.
            css=""    :        css style to h2.
        """
        self.html += "\n" + f"<h2 style='{css}'>{x}</h2>"
    def h3(self,  x,css: str=''):
        """  Add h3 to html
        Docs::

            x         :        text to place inside html tag.
            css=""    :        css style to h3.
        """
        self.html += "\n" + f"<h3 style='{css}'>{x}</h3>"
    def h4(self,  x,css: str='')  : 
        """  Add h4 to html
        Docs::

            x         :        text to place inside html tag.
            css=""    :        css style to h4.
        """
        self.html += "\n" + f"<h4 style='{css}'>{x}</h4>"
    def p(self,   x,css: str=''):
        """  Add p to html
        Docs::

            x         :        text to place inside html tag.
            css=""    :        css style to p.
        """
        self.html += "\n" + f"<p style='{css}'>{x}</p>"
    def div(self, x,css: str=''): 
        """  Add div to html
        Docs::

            x         :        text to place inside html tag.
            css=""    :        css style to div.
        """
        self.html += "\n" + f"<div style='{css}'>{x}</div>"
    def hr(self,    css: str=''):
        """  Add horizontal row to html
        Docs::

            css=""    :        css style to hr.
        """
        self.html += "\n" + f"<hr style='{css}'/>"
    def sep(self,   css: str=''): 
        """  Add separator to html
        Docs::

            css=""    :        css style to sep.
        """
        self.html += "\n" + f"<hr style='{css}'/>"
    def br(self,    css: str=''): 
        """  Add break to html
        Docs::

            css=""    :        css style to br.
        """
        self.html += "\n" + f"<br style='{css}'/>"

    def get_html(self)-> str:
        """  Funtion to return html text created
        """
        full = self.head  + self.html + self.tail
        return full

    def print(self):
        """  Print html text created
        """
        full = self.head  + self.html + self.tail
        print(full, flush=True)

    def save(self, dir_out=None):
        """  Save html file
        Docs::

                dir_out="./myexport/":        Name of the output file. Defaults to None.
        """ 

        self.dir_out = dir_out if dir_out is not None else self.dir_out
        self.dir_out = dir_out.replace("\\", "/")
        self.dir_out = os.getcwd() + "/" + self.dir_out if "/" not in self.dir_out[0] else self.dir_out
        os.makedirs( os.path.dirname(self.dir_out) , exist_ok = True )

        full = self.head + self.html + self.tail
        with open(self.dir_out, mode='w') as fp:
            fp.write(full)

    def open_browser(self):
        """ Open html file in browser
        """
        if os.name == 'nt':
            os.system(f'start chrome "file:///{self.dir_out}" ')
            ### file:///D:/_devs/Python01/gitdev/myutil/utilmy/viz/test_viz_table.html   

    def serve_file(self):       
        full = self.head + self.html + self.tail

        # import flask
        import flask
        from flask import Flask
        app = Flask(__name__)

        @app.route("/")
        def get_report():
            return full

        app.run()
        
    def add_css(self, css):
        """  Add custom to file
        Docs::

                css="None":        css str
        """ 
        data = f"\n<style>\n{css}\n</style>\n"
        self.head += data
    
    def add_js(self,js):
        """  Add custom js to file
        Docs::

                js="None":        js str
        """ 
        data = f"\n<script>\n{js}\n</script>\n"
        self.tail = data + self.tail

    def hidden(self, x,css: str=''):
        """  Add toggled hidden div to html
        Docs::

            x         :        text to place inside html tag.
            css=""    :        css style to hidden.
        """
        # Hidden P paragraph
        custom_id = str(random.randint(9999,999999))
        # self.head += "\n" + js_code.js_hidden  # Hidden  javascript
        self.html += "\n" + f"<div id='div{custom_id}' style='{css}'>{x}</div>"
        button     = """<button id="{btn_id}">Toggle</button>""".format(btn_id="btn"+custom_id)
        self.html += "\n" + f"{button}"        
        js         = """function toggle() {{
                if (document.getElementById("{div_id}").style.visibility === "visible") {{
                  document.getElementById("{div_id}").style.visibility = "hidden"
                }} else {{
                  document.getElementById("{div_id}").style.visibility = "visible"
                }}
              }}
              document.getElementById('{btn_id}').addEventListener('click', toggle);""".format(btn_id="btn"+custom_id,
                div_id="div"+custom_id)
        self.add_js(js)


    def table(self, df:pd.DataFrame, format: str='blue_light', custom_css_class=None,colimage = None, use_datatable=False, table_id=None, **kw):
        """  Show Pandas in HTML and interactive
        ## show table in HTML : https://pypi.org/project/pretty-html-table/
        Docs::

                format="blue_light"  :        List of colors available at https://pypi.org/project/pretty-html-table/
                custom_css_class=None:        Add custom class for table
                use_datatable=None   :        Create html table as a database
                table_id=None        :        Id for table tag
        """
        if colimage:
            colimage = [colimage] if isinstance(colimage, str) else colimage
            for ci in colimage : 
               df[ci] = df[ci].map('<img src="{}" width="50px" height="50px">'.format)
               
        import pretty_html_table
        html_code = pretty_html_table.build_table(df, format)
        table_id  = random.randint(9999,999999) if table_id is None else table_id  #### Unique ID

        # add custom CSS class
        if custom_css_class:
            html_code = html_code.replace('<table', f'<table class="{custom_css_class}"')
               
        if use_datatable:
            # JS add datatables library
            self.head = self.head + """
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/dt-1.10.25/datatables.min.css"/>
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
            <script type="text/javascript" src="https://cdn.datatables.net/v/dt/dt-1.10.25/datatables.min.js"></script>"""
            # https://datatables.net/manual/installation
            # add $(document).ready( function () {    $('#table_id').DataTable(); } );

            # add data table
            html_code = html_code.replace('<table', f'<table id="{table_id}" ')
            html_code += """\n<script>$(document).ready( function () {    $('#{mytable_id}').DataTable({
                            "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]]
                           }); 
                           });\n</script>\n
                         """.replace('{mytable_id}', str(table_id))
        if colimage:
            html_code = html_code.replace('&lt;','<')
            html_code = html_code.replace('&gt;','>')
            html_code = html_code.replace('width: auto"></td>','width: auto">&nbsp;</td>')
        self.html += "\n\n" + html_code


    def plot_tseries(self, df:pd.DataFrame, coldate, coly1: list, coly2=[],
                     title: str="", xlabel=None, y1label=None,  y2label=None,                      
                     figsize: tuple=(800,400),  plot_type="", spacing=0.1,

                     date_format=None, nsample: int= 10000,
                     
                     cfg: dict = {}, mode: str='highcharts', save_img="",  **kw):
        """  Create html time series chart.
        Docs::

                df               :        Dataframe with date and columns of interest.
                coldate          :        Column name for date.
                coly1            :        List of column names for y1.
                coly2=[]         :        List of column names for y2.
                title=""         :        Title of the chart.
                xlabel=None      :        Label for x-axis.
                y1label=None     :        Label for y1-axis.
                y2label=None     :        Label for y2-axis.
                figsize="(14,7)" :        Size of the figure.
                plot_type=""     :        Type of plot.
                spacing=0.1      :        Spacing between subplots.
                date_format=None :        Date format.
                nsample=10000    :        Number of samples.
                cfg={}           :        Configuration for plot.
                mode='highcharts':        Mode of plot.
                save_img=""      :        Name of the image to save.
        """
        html_code = ''
        if mode == 'matplot':
            import mpld3
            fig       = pd_plot_tseries_matplot(df, coldate, coly1=coly1, coly2=coly2,
                                                   date_format=date_format,

                                                   title=title, xlabel=xlabel, y1label=y1label, y2label=y2label,
                                                   figsize=figsize,  spacing=spacing,

                                                   cfg=cfg, mode=mode, save_img=save_img, verbose=self.verbose )
            html_code = mpld3.fig_to_html(fig)

        elif mode == 'highcharts':
            html_code = pd_plot_tseries_highcharts(df, coldate, coly1=coly1, coly2=coly2,
                                                   date_format=date_format,

                                                   title=title, xlabel=xlabel, y1label=y1label, y2label=y2label,
                                                   figsize=figsize,  spacing=spacing,

                                                   cfg=cfg, mode=mode, save_img=save_img, verbose=self.verbose  )
        self.html += "\n\n" + html_code


    def plot_network_highcharts(self, df:pd.DataFrame, col, width=1, marker_fill_color='#FFFFFF', marker_line_width=2, marker_line_color='#A53E32',
                       link_width=2, link_color='#A53E32', link_length=80, link_dash_style='dash', title: str=''):
        """  Create html network chart.
        Docs::
                df                        :        Dataframe with date and columns of interest. 
                col                       :        Array of Column name for network.
                width=1                   :        Width of the network.
                marker_fill_color='#FFFFFF':        Marker fill color.
                marker_line_width=2       :        Marker line width.
                marker_line_color='#A53E32':        Marker line color.
                link_width=2              :        Link width.
                link_color='#A53E32'      :        Link color.
                link_length=80            :        Link length.
             
                link_dash_style='dash'    :        Link dash style.
                title=""                  :        Title of the chart.
        """

        container_id = 'cid_' + str(np.random.randint(9999, 99999999))

        code_html_start = f"""
         <script src="https://code.highcharts.com/modules/networkgraph.js"></script>
             <div id="{container_id}">Loading</div>
         <script>
        """

        data = [ list(t) for t in df[col].values ]

        data_code = """
            var data = {data}
            """.format(data = data)
        
        title  = """{ text:'""" + title +"""' }"""

        plot_border_width = width  # Customize the width

        chart = """{
            type: 'networkgraph',
            plotBorderWidth: """ + f"{plot_border_width}" + """
            }
        """

        # Customize marker properties
        marker_properties = f"""
        marker: {{
            fillColor: '{marker_fill_color}',
            lineWidth: {marker_line_width},
            lineColor: '{marker_line_color}'
        }},
        """

        # Customize link properties
        link_properties = f"""
        link: {{
            width: {link_width},
            color: '{link_color}',
            length: {link_length},
            dashStyle: '{link_dash_style}'
        }},
        """

        series = f"""[{{
            color: '#A53E32',
            {link_properties}
            name: 'K8',
            data: data,
            {marker_properties}
        }}]"""

        js_code = """Highcharts.chart('"""+container_id+"""', {
            chart:""" + chart +""",
            title:""" +  title+""",
            series: """+ series +"""
        });
        </script>"""

        html_code = data_code + js_code

        html_code = code_html_start + html_code

        self.html += "\n\n" + html_code
    
    def plot_parallel_highcharts(self, df:pd.DataFrame, col, width=2, marker_enabled=False, marker_states_hover_enabled=False,
                           marker_states_hover_halo_size=0, colors=['#ff0000'], title: str=''):
        """  Create html parallel chart.
        Docs::
                df                                     :        Dataframe with date and columns of interest.
                col                                    :        Array of Column name for parallel chart.
                width=2                                :        Width of the parallel chart.
                marker_enabled=False                   :        Marker enabled.
                marker_states_hover_enabled=False      :        Marker states hover enabled.
                marker_states_hover_halo_size=0        :        Marker states hover halo size.
                colors=['rgba(11, 200, 200, 0.1)']     :        Colors of the parallel chart.
                title=""                               :        Title of the chart.
        """
        
        container_id = 'cid_' + str(np.random.randint(9999, 99999999))

        code_html_start = f"""
            <script src="https://code.highcharts.com/modules/parallel-coordinates.js"></script>
                <div id="{container_id}">Loading</div>
            <script>
        """

        data = [ list(t) for t in df[col].values ]

        data_code = """
            var data = {data}
        """.format(data = data)

        chart =  f"""{{
            type: 'spline',
            parallelCoordinates: true,
            parallelAxes: {{
                lineWidth: {width}
            }}
        }}"""

        title  = """{ text:'""" + title +"""' }"""

        plotOptions= """
            {
            series: {
                accessibility: {
                enabled: false
                },
                animation: false,
                marker: {
                enabled: """ + str(marker_enabled).lower() + """,
                states: {
                    hover: {
                    enabled: """ + str(marker_states_hover_enabled).lower() + """
                    }
                }
                },
                states: {
                hover: {
                    halo: {
                    size: """ + str(marker_states_hover_halo_size) + """
                    }
                }
                },
                events: {
                mouseOver: function () {
                    this.group.toFront();
                }
                }
            }
            }
        """

        tooltip = F"""{{
            pointFormat: '<span style="color:{'point.color'}"></span>' +
                '{{series.name}}: <b>{{point.formattedValue}}</b><br/>'
        }}"""
        
        x_axis = f"""{{
            offset: 10,
            categories: {col},
        }}"""

        colors =  """['""" + "','".join(colors) + """']"""

        series = """
        data.map(function (set, i) {
                return {
                name: i,
                data: set,
                shadow: false
                };
            })
        """

        js_code = """Highcharts.chart('"""+container_id+"""', {
            chart:""" + chart +""",
            title:""" +  title+""",
            plotOptions:""" +  plotOptions+""",
            tooltip:""" +  tooltip+""",
            xAxis:""" +  x_axis+""",
            colors:""" +  colors+""",
            series: """+ series +"""
        });
        </script>"""

        html_code = data_code + js_code

        html_code = code_html_start + html_code

        print(html_code)

        self.html += "\n\n" + html_code
    

    def plot_histogram(self, df:pd.DataFrame, col,
                       title: str='', xlabel: str=None, ylabel: str=None,
                       figsize: tuple=None, colormap:str = 'RdYlBu', 
                       nsample=10000,binWidth=None,color:str='#7CB5EC',
                       nbin=10, q5=0.005, q95=0.95,cfg: dict = {}, 
                       mode: str='matplot', save_img="",  **kw):
        """  Create html histogram chart.
        Docs::

                df               :        Dataframe with date and columns of interest.
                col              :        Column name for histogram.
                title=''         :        Title of the chart.
                xlabel=None      :        Label for x-axis.
                ylabel=None      :        Label for y-axis.
                figsize=None     :        Size of the figure. Defaults to (14,7).
                colormap='RdYlBu':        Colormap code.
                nsample=10000    :        Number of samples.
                binWidth=None    :        Bin width.
                color='#7CB5EC'  :        Color of the histogram.
                nbin=10          :        Number of bins.
                q5=0.005         :        Quantile 5.
                q95=0.95         :        Quantile 95.
                cfg={}           :        Configuration for plot.
                mode='matplot'   :        Mode of plot.
        """
        html_code = ''
        if mode == 'matplot':
            fig       = pd_plot_histogram_matplot(df, col,
                                                  title=title, xlabel= xlabel, ylabel=ylabel,
                                                  colormap=colormap, nsample=nsample,
                                                  nbin=nbin, q5=q5, q95=q95,
                                                  cfg=cfg, mode=mode, save_img=save_img, verbose=self.verbose  )
            html_code = self.fig_to_html(fig)

        elif mode == 'highcharts':
            cfg['figsize'] = figsize
            html_code = pd_plot_histogram_highcharts(df, col,
                                                     title=title, xaxis_label=xlabel, yaxis_label=ylabel,
                                                     colormap=colormap, nsample=nsample,
                                                     binsNumber=nbin,binWidth=binWidth,color=color,
                                                     cfg=cfg,mode=mode,save_img=save_img, verbose=self.verbose  )
        self.html += "\n\n" + html_code


    def plot_scatter(self, df:pd.DataFrame, colx, coly,
                     collabel=None, colclass1=None, colclass2=None, colclass3=None,                     
                     title: str='',                      
                     figsize: tuple='', 
                     nsample: int=10000,
                     cfg: dict = {}, mode: str='matplot', save_img='', **kw):
        """  Create html scatter chart.
        Docs::

                df            :        Dataframe with date and columns of interest.
                colx          :        Column name for x-axis.
                coly          :        Column name for y-axis.
                collabel=None :        Label for x-axis.
                title=''      :        Title of the chart
                figsize=''    :        Size of the figure.
                nsample=10000 :        Number of samples.
                cfg={}        :        Configuration for plot.
                mode='matplot':        Mode of plot.
        """
        html_code = ''
        if mode == 'matplot':
            html_code = pd_plot_scatter_matplot(df, colx=colx, coly=coly,
                                                collabel=collabel,
                                                colclass1=colclass1, colclass2=colclass2, colclass3=colclass3,
                                                nsample=nsample,
                                                cfg=cfg, mode=mode, save_img=save_img, verbose= self.verbose )

        elif mode == 'highcharts':
            html_code = pd_plot_scatter_highcharts(df, colx= colx, coly=coly,
                                                   collabel=collabel,
                                                   colclass1=colclass1, colclass2=colclass2, colclass3=colclass3,
                                                   nsample=nsample,
                                                   cfg=cfg, mode=mode, save_img=save_img, verbose=self.verbose )

        self.html += "\n\n" + html_code
      
    def plot_density(self, df: pd.DataFrame, colx, coly, radius=9,
                     title: str = 'Plot Density',
                     figsize: tuple = (460, 460), xlabel: str = 'x-axis', ylabel: str = 'y-axis', color: str = '#69b3a2',
                     cfg: dict = {}, mode: str = 'd3', **kw):
        """  Create html density chart.
        Docs::

                df                  :        Dataframe with date and columns of interest.
                colx                :        Column name for x-axis.
                coly                :        Column name for y-axis.
                radius=9            :        Radius of the circle.
                title='Plot Density':        Title of the chart.
                figsize=(460, 460)  :        Size of the figure.
                xlabel='x-axis'     :        Label for x-axis.
                ylabel='y-axis'     :        Label for y-axis.
                color='#69b3a2'     :        Color of the circle.
                cfg={}              :        Configuration for plot.
                mode='d3'           :        Mode of plot.
        """
      
        html_code = ''
        if mode == 'd3':
            html_code = pd_plot_density_d3(df, colx, coly, radius, title, figsize, xlabel, ylabel, color, cfg)
        self.html += "\n\n" + html_code 
      
    def plot_parallel(self, df: pd.DataFrame, col=[],
                    title: str =[],
                    figsize: tuple = (460, 460), color: str = '#69b3a2',
                    cfg: dict = {}, mode: str = 'd3', **kw):
        """  Create html density chart.
        Docs::

            df                :        Dataframe with date and columns of interest.
            col=[]            :        List of columns.
            title=[]          :        Title of the chart.
            figsize=(460, 460):        Size of the figure.
            color='#69b3a2'   :        Color of the circle.
            cfg={}            :        Configuration for plot.
            mode='d3'         :        Mode of plot.
        """

        html_code = ''
        if mode == 'd3':
            html_code = pd_plot_parallel_d3(df, col, title, figsize, color, cfg)
        self.html += "\n\n" + html_code  

      
    def images_dir(self, dir_input="*.png",  title: str="", 
                   verbose:bool =False):
        """  Convert images to html code and add it to html.
        Docs::

            dir_input="*.png" :        Directory with images.
            title=''           :        Title of the chart.
            verbose=False      :        Verbose mode.
        """
        html_code = images_to_html(dir_input=dir_input,  title=title, verbose=verbose)
        self.html += "\n\n" + html_code


    def pd_plot_network(self, df:pd.DataFrame, cola:    str='col_node1', colweight:str="weight",
                        colb: str='col_node2', coledge: str='col_edge'):
        """  Add graph to html page
        Docs::

            df:        Panda dataframe
            cola='col_node1'  :        cola from df.
            colweight="weight":        weigth of edges.
            colb='col_node2'  :        colb from df.
            coledge='col_edge':        edge from df.
        """ 

        head, body = pd_plot_network(df, cola=cola, colb=colb,colweight=colweight, coledge=coledge)
        self.html += "\n\n" + body
        self.head += "\n\n" + head

    def pd_plot_network_cyto(self, df:pd.DataFrame, cola:    str='col_node1', colweight:str="weight",
                             colb: str='col_node2', coledge: str='col_edge'):
        """  Add graph to html page
        Docs::

            df:        Panda dataframe
            cola='col_node1'  :        cola from df.
            colweight="weight":        weigth of edges.
            colb='col_node2'  :        colb from df.
            coledge='col_edge':        edge from df.
        """ 
        head, body = pd_plot_network_cyto(df, cola=cola, colb=colb,colweight=colweight, coledge=coledge)
        self.html += "\n\n" + body
        self.head += "\n\n" + head



##################################################################################################################
######### MLPD3 Display ##########################################################################################
mpld3_CSS = """
    text.mpld3-text, div.mpld3-tooltip {
      font-family:Arial, Helvetica, sans-serif;
    }
    g.mpld3-xaxis, g.mpld3-yaxis {
    display: none; }
"""

try:
    import mpld3
    class mpld3_TopToolbar(mpld3.plugins.PluginBase):
        """Plugin for moving toolbar to top of figure"""

        JAVASCRIPT = """
        mpld3.register_plugin("toptoolbar", TopToolbar);
        TopToolbar.prototype = Object.create(mpld3.Plugin.prototype);
        TopToolbar.prototype.constructor = TopToolbar;
        function TopToolbar(fig, props){
            mpld3.Plugin.call(this, fig, props);
        };
        TopToolbar.prototype.draw = function(){
          // the toolbar svg doesn't exist
          // yet, so first draw it
          this.fig.toolbar.draw();
          // then change the y position to be
          // at the top of the figure
          this.fig.toolbar.toolbar.attr("x", 150);
          this.fig.toolbar.toolbar.attr("y", 400);
          // then remove the draw function,
          // so that it is not called again
          this.fig.toolbar.draw = function() {}
        }
        """
        def __init__(self):
            self.dict_ = {"type": "toptoolbar"}
except : pass



def mlpd3_add_tooltip(fig, points, labels):
    """  Add tooltip to a figure.
    Docs::

            fig (mpld3.Figure): Figure to add tooltip to.
            points (list): List of points to add tooltip to.
            labels (list): List of labels to add tooltip to.
    """

    # set tooltip using points, labels and the already defined 'css'
    tooltip = mpld3.plugins.PointHTMLTooltip(
        points[0], labels, voffset=10, hoffset=10, css=mpld3_CSS)
    # connect tooltip to fig
    mpld3.plugins.connect(fig, tooltip, mpld3_TopToolbar())


def pd_plot_scatter_get_data(df0:pd.DataFrame,colx: str=None, coly: str=None, collabel: str=None,
                            colclass1: str=None, colclass2: str=None, nmax: int=20000, **kw):
    """  Get data for scatter plot.
    Docs::

            df0           :        Dataframe with data.
            colx=None     :        Column name for x-axis.
            coly=None     :        Column name for y-axis.
            collabel=None :        label per point.
            colclass1=None:        Color per point class1.
            colclass2=None:        Size per point class2.
            nmax=20000    :        Maximum number of points.
    """
    # import copy
    nmax = min(nmax, len(df0))
    df   = df0.sample(nmax)

    colx      = 'x'      if colx is None else colx
    coly      = 'y'      if coly is None else coly
    collabel  = 'label'  if collabel is None else collabel    ### label per point
    colclass1 = 'class1' if colclass1 is None else colclass1  ### Color per point class1
    colclass2 = 'class2' if colclass2 is None else colclass2  ### Size per point class2

    #######################################################################################
    for ci in [ collabel, colclass1, colclass2 ] :
       if ci  not in df.columns : df[ci]  = ''
       df[ci]  = df[ci].fillna('')

    #######################################################################################
    xx = df[colx].values
    yy = df[coly].values

    # label_list = df[collabel].values
    label_list = ['{collabel} : {value}'.format(collabel=collabel,value =  df0[collabel][i]) for i in range(len(df0[collabel]))]

    ### Using Class 1 ---> Color
    color_scheme = [ 0,1,2,3]
    n_colors     = len(color_scheme)
    color_list   = [  color_scheme[ hash(str( x)) % n_colors ] for x in df[colclass1].values     ]


    ### Using Class 2  ---> Color
    n_size      = len(df[colclass2].unique())
    smin, smax  = 100.0, 200.0
    size_scheme = np.arange(smin, smax, (smax-smin)/n_size)
    n_colors    = len(size_scheme)
    size_list   = [  size_scheme[ hash(str( x)) % n_colors ] for x in df[colclass2].values     ]


    ###
    ptype_list = []

    return xx, yy, label_list, color_list, size_list, ptype_list



def pd_plot_scatter_matplot(df:pd.DataFrame, colx: str=None, coly: str=None, collabel: str=None,
                            colclass1: str=None, colclass2: str=None,
                            cfg: dict = {}, mode='d3', save_path: str='', verbose=True,  **kw)-> str:
    """  Plot scatter plot.
    Docs::

            df0           :        Dataframe with data.
            colx=None     :        Column name for x-axis.
            coly=None     :        Column name for y-axis.
            collabel=None :        label per point.
            colclass1=None:        Color per point class1.
            colclass2=None:        Size per point class2.
            cfg={}        :        Configuration dictionary.
            mode='d3'     :        Mode: 'd3' or 'matplotlib'.
            save_path=''  :        Path to save plot.
            verbose=True  :        Verbose.
    """
    import matplotlib.pyplot as plt
    cc           = Box(cfg)
    cc.figsize   = cc.get('figsize', (25, 15))  # Dict type default values
    cc.title     = cc.get('title', 'scatter title' )

    #######################################################################################
    xx, yy, label_list, color_list, size_list, ptype_list = pd_plot_scatter_get_data(df,colx, coly, collabel,
                                                            colclass1, colclass2)

    # set up plot
    fig, ax = plt.subplots(figsize= cc.figsize)  # set size
    ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling
    scatter = ax.scatter(xx,
                     yy,
                     c=color_list,
                     s=size_list,
                     alpha=1,
                     cmap=plt.cm.jet)
    ax.grid(color='white', linestyle='solid')
    # ax.scatter(xx, yy, s= size_list, label=label_list,
    #         c=color_list)
    ax.set_aspect('auto')
    ax.tick_params(axis='x',        # changes apply to the x-axis
                   which='both',    # both major and minor ticks are affected
                   bottom='off',    # ticks along the bottom edge are off
                   top='off',       # ticks along the top edge are off
                   labelbottom='off')
    ax.tick_params(axis='y',  # changes apply to the y-axis
                   which='both',  # both major and minor ticks are affected
                   left='off',  # ticks along the bottom edge are off
                   top='off',  # ticks along the top edge are off
                   labelleft='off')

    # ax.legend(numpoints=1)  # show legend with only 1 point
    # label_list = ['{0}'.format(d_small['Name'][i]) for i in range(N)]
    # add label in x,y position with the label
    # for i in range(N):
    #     ax.text(df['Age'][i], df['Fare'][i], label_list[i], size=8)
    
    if len(save_path) > 1 :
        plt.savefig(f'{cc.save_path}-{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.png', dpi=200)

    
    ax.set_aspect('auto')

    #  uncomment to hide tick
    # set tick marks as blank
    # ax.axes.get_xaxis().set_ticks([])
    # ax.axes.get_yaxis().set_ticks([])

    # set axis as blank
    # ax.axes.get_xaxis().set_visible(False)
    # ax.axes.get_yaxis().set_visible(False)
    
    # connect tooltip to fig
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=label_list, voffset=10, hoffset=10)
    mpld3.plugins.connect(fig, tooltip, mpld3_TopToolbar())
    # mlpd3_add_tooltip(fig, points, label_list)
    

    # ax.legend(numpoints=1)  # show legend with only one dot
    # mpld3.save_html(fig,  f"okembeds.html")
    # return fig
    ##### Export ############################################################
    html_code = mpld3.fig_to_html(fig)
    # print(html_code)
    return html_code
   

def pd_plot_density_d3(df: pd.DataFrame, colx, coly, radius=9,
                       title: str = 'Plot Density',
                       figsize: tuple = (460, 460), xlabel: str = 'x-axis', ylabel: str = 'y-axis',
                       color: str = '#69b3a2',
                       cfg: dict = {}):
    """  Plot density plot.
    Docs::

            df0                 :        Dataframe with data.
            colx=None           :        Column name for x-axis.
            coly=None           :        Column name for y-axis.
            radius=9            :        Radius of the circle.
            title='Plot Density':        Title of the plot.
            figsize=(460, 460)  :        Size of the figure.
            xlabel='x-axis'     :        Label of the x-axis.
            ylabel='y-axis'     :        Label of the y-axis.
            color='#69b3a2'     :        Color of the circle.
            cfg={}              :        Configuration dictionary.
    """
    container_id = 'cid_' + str(np.random.randint(9999, 99999999))
    html_code = f'<div id="{container_id}"></div>'

    df = df.rename({colx: 'x', coly: 'y'}, axis=1)

    df.loc[:, 'x'] = df['x'].fillna(0)
    df.loc[:, 'x'] = [to_float(t) for t in df['x'].values]

    df.loc[:, 'y'] = df['y'].fillna(0)
    df.loc[:, 'y'] = [to_float(t) for t in df['y'].values]

    # panda find max and min value of colx and coly
    x_max = df['x'].max()
    x_min = df['x'].min()
    y_max = df['y'].max()
    y_min = df['y'].min()
    width = figsize[0]
    height = figsize[1]

    # panda total number of point
    n_point = df.shape[0]

    print(x_max, x_min, y_max, y_min, n_point)

    # number of point in bins
    n_point_helper = 5 if n_point < 100 else 20
    n_point = int(n_point * (n_point // n_point_helper) / ((width) * (height) / (3.14 * radius * radius)))

    if n_point == 0:
        n_point = 1

    data = df[['x', 'y']].to_json(orient='records')

    html_code += '''
        <script>
            // set the dimensions and margins of the graph
            margin = {{ top: 10, right: 30, bottom: 30, left: 40 }},
                width = {width} - margin.left - margin.right,
                height = {height} - margin.top - margin.bottom;
            // append the svg object to the body of the page
            svg = d3.select("#{container_id}")
            .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
            .append("g")
                .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")");
            svg.append("text")
               .attr("x", width/2)
               .attr("y", margin.top)
               .attr("text-anchor", "middle")
               .style("font-size", "16px")
               .text("{title}");
            svg.append("text")
               .attr("transform", "translate(" + (460/2) + " ," + (460-10) + ")")
               .style("text-anchor", "middle")
               .text("{xlabel}");
            svg.append("text")
           .attr("transform", "rotate(-90)")
           .attr("x", -(height/2))
           .attr("y", -30)
           .style("text-anchor", "middle")
           .text("{ylabel}");
            data = {data}
            console.log(data);
            // Add X axis
            x = d3.scaleLinear()
                .domain([{x_min}, {x_max}])
                .range([ 0, width ]);
            svg.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(x));
            // Add Y axis
            y = d3.scaleLinear()
                .domain([{y_min}, {y_max}])
                .range([ height, 0 ]);
            svg.append("g")
                .call(d3.axisLeft(y));
            // Reformat the data: d3.hexbin() needs a specific format
            inputForHexbinFun = []
            data.forEach(function(d) {{
                inputForHexbinFun.push( [x(d.x), y(d.y)] )  // Note that we had the transform value of X and Y !
            }})
            // Prepare a color palette
            color = d3.scaleLinear()
                .domain([0, {n_point}]) // Number of points in the bin?
                .range(["transparent",  "{color}"]);
            // Compute the hexbin data
            hexbin = d3.hexbin()
                .radius({radius}) // size of the bin in px
                .extent([ [0, 0], [width, height] ])
            // Plot the hexbins
            svg.append("clipPath")
                .attr("id", "clip")
                .append("rect")
                .attr("width", width)
                .attr("height", height)
            svg.append("g")
                .attr("clip-path", "url(#clip)")
                .selectAll("path")
                .data( hexbin(inputForHexbinFun) )
                .enter().append("path")
                .attr("d", hexbin.hexagon())
                .attr("transform", function(d) {{ return "translate(" + d.x + "," + d.y + ")"; }})
                .attr("fill", function(d) {{ return color(d.length); }})
                .attr("stroke", "black")
                .attr("stroke-width", "0.1")
        </script>
    '''.format(data=data, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, n_point=n_point,
               container_id=container_id,
               radius=radius, width=width, height=height, title=title, xlabel=xlabel, ylabel=ylabel, color=color)

    return html_code


def pd_plot_parallel_d3(df: pd.DataFrame,
                        col = [],
                         title: str = '',
                         figsize: tuple = (460, 460),
                         color: str = '#69b3a2',
                        cfg: dict = {}):
    """ Plot parallel coordinate using d3.
    Docs::

        df                :        pandas.DataFrame.
        col=[]            :        List of column names.
        title=''          :        Title of the plot..
        figsize=(460, 460):        Size of the figure.
        color='#69b3a2'   :        Color of the plot.
        cfg={}            :        Configuration dictionary.
    """
    container_id = 'cid_' + str(np.random.randint(9999, 99999999))
    html_code = f'<div id="{container_id}"></div>'

    width = figsize[0]
    height = figsize[1]

    # check col is empty or string
    if isinstance(col, str):
        col = [col]
    if len(col) == 0:
        col = df.columns.tolist()

    # print(col,"col")
    for i in col:
        df.loc[:, i] = df[i].fillna(0)
        df.loc[:, i] = [to_float(t) for t in df[i].values]

    data = df[col].to_json(orient='records')

    html_code += '''
        <script>
    
          // set the dimensions and margins of the graph
          var margin = {{ top: 30, right: 10, bottom: 10, left: 0 }},
            width = {width} - margin.left - margin.right,
            height = {height} - margin.top - margin.bottom;
    
          // append the svg object to the body of the page
          var svg = d3.select("#{container_id}")
          .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform",
                  "translate(" + margin.left + "," + margin.top + ")");
                  
          svg.append("text")
               .attr("x", width/2)
               .attr("text-anchor", "middle")
               .style("font-size", "16px")
               .text("{title}");
            
          
        // Parse the Data
        data = {data}  
            
        // Extract the list of dimensions we want to keep in the plot. Here I keep all except the column called Species
        dimensions = d3.keys(data[0]).filter(function(d) {{ 
          col = {col};
          if(col.includes(d)){{
            return d 
          }}  
        }})

        // For each dimension, I build a linear scale. I store all in a y object
        var y = {{}}
        for (i in dimensions) {{
          name = dimensions[i]
          y[name] = d3.scaleLinear()
            .domain( d3.extent(data, function(d) {{ return +d[name]; }}) )
            .range([height, 0])
        }}

        // Build the X scale -> it find the best position for each Y axis
        x = d3.scalePoint()
          .range([0, width])
          .padding(1)
          .domain(dimensions);

        // The path function take a row of the csv as input, and return x and y coordinates of the line to draw for this raw.
        function path(d) {{
            return d3.line()(dimensions.map(function(p) {{ return [x(p), y[p](d[p])]; }}));
        }}

        // Draw the lines
        svg
          .selectAll("myPath")
          .data(data)
          .enter().append("path")
          .attr("d",  path)
          .style("fill", "none")
          .style("stroke", "{color}")
          .style("opacity", 0.5)

        // Draw the axis:
        svg.selectAll("myAxis")
          // For each dimension of the dataset I add a 'g' element:
          .data(dimensions).enter()
          .append("g")
          // I translate this element to its right position on the x axis
          .attr("transform", function(d) {{ return "translate(" + x(d) + ")"; }})
          // And I build the axis with the call function
          .each(function(d) {{ d3.select(this).call(d3.axisLeft().scale(y[d])); }})
          // Add axis title
          .append("text")
            .style("text-anchor", "middle")
            .attr("y", -9)
            .text(function(d) {{ return d; }})
            .style("fill", "black")
    
    
        </script>
    '''.format(col=col, container_id=container_id, data=data, color=color, width=width, height=height, title=title)

    return html_code


def pd_plot_histogram_matplot(df:pd.DataFrame, col: str='' ,colormap:str='RdYlBu', title: str='', nbin=20.0, q5=0.005, q95=0.995, nsample=-1,
                              save_img: str="",xlabel: str=None,ylabel: str=None, verbose=True, **kw):
    """ Plot histogram using matplotlib.
    Docs::

        df                :        Dataframe with data.
        col=''            :        Column name for histogram.
        colormap='RdYlBu' :        Colormap for histogram.
        title=''          :        Title of the plot.
        nbin=20.0         :        Number of bins.
        q5=0.005          :        Quantile 5.
        q95=0.995         :        Quantile 95.
        nsample=-1        :        Number of samples to draw.
        save_img=''       :        Path to save the image.
        xlabel=None       :        Label for x axis.
        ylabel=None       :        Label for y axis.
        verbose=True      :        Verbose mode.
    """
    import matplotlib.pyplot as plt
    cm = plt.cm.get_cmap(colormap)
    df.loc[:,col] = df[col].fillna(0)
    df.loc[:,col] = [ to_float(t) for t in df[col].values  ]
    dfi = df[col]
    q0  = dfi.quantile(q5)
    q1  = dfi.quantile(q95)

    fig = plt.figure()

    if nsample < 0:
        n, bins, patches = plt.hist(dfi, bins=np.arange(q0, q1,  (q1 - q0) / nbin))
        # dfi.hist(bins=np.arange(q0, q1,  (q1 - q0) / nbin))
    else:
        n, bins, patches = plt.hist(dfi.sample(n=nsample, replace=True), bins=np.arange(q0, q1,  (q1 - q0) / nbin))
        # dfi.sample(n=nsample, replace=True).hist( bins=np.arange(q0, q1,  (q1 - q0) / nbin))
    for i, p in enumerate(patches):
        plt.setp(p, 'facecolor', cm(i/nbin))
    plt.title(title)
    plt.xlabel(xlabel) 
    plt.ylabel(ylabel)

    if len(save_img)>0 :
        os.makedirs(os.path.dirname(save_img), exist_ok=True)
        plt.savefig(save_img)
        print(save_img)

    # plt.close(fig)
    return fig



def pd_plot_tseries_matplot(df:pd.DataFrame, plot_type: str=None, coly1: list = [], coly2: list = [],
                            figsize: tuple =(8, 4), spacing=0.1, verbose=True, **kw):
    """  Plot t-series chart using matplot.
    Docs::

        df               :        Dataframe with date and columns of interest.
        plot_type        :        Type of plot.
        coly1            :        List of column names for y1.
        coly2=[]         :        List of column names for y2.
        title=""         :        Title of the chart.
        figsize="(14,7)" :        Size of the figure.
        spacing=0.1      :        Spacing between subplots.
        verbose=True     :        Verbose mode.
    """
    from pandas import plotting
    from pandas.plotting import _matplotlib
    from matplotlib import pyplot as plt

    plt.figure(figsize=figsize)
    # Get default color style from pandas - can be changed to any other color list
    if coly1 is None:
        coly1 = df.columns
    if len(coly1) == 0:
        return
    colors = getattr(getattr(plotting, '_matplotlib').style, '_get_standard_colors')(
        num_colors=len(coly1 + coly2))

    # Displays subplot's pair in case of plot_type defined as `pair`
    if plot_type == 'pair':
        ax = df.plot(subplots=True, figsize=figsize, **kw)
        # plt.show()
        html_code = mpld3.fig_to_html(ax,  **kw)
        return html_code

    # First axis
    ax = df.loc[:, coly1[0]].plot(
        label=coly1[0], color=colors[0], **kw)
    ax.set_ylabel(ylabel=coly1[0])
    ##  lines, labels = ax.get_legend_handles_labels()
    lines, labels = [], []

    i1 = len(coly1)
    for n in range(1, len(coly1)):
        df.loc[:, coly1[n]].plot(
            ax=ax, label=coly1[n], color=colors[(n) % len(colors)], **kw)
        line, label = ax.get_legend_handles_labels()
        lines += line
        labels += label

    for n in range(0, len(coly2)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        df.loc[:, coly2[n]].plot(
            ax=ax_new, label=coly2[n], color=colors[(i1 + n) % len(colors)], **kw)
        ax_new.set_ylabel(ylabel=coly2[n])

        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

    ax.legend(lines, labels, loc=0)
    #plt.show()
    return ax
    # html_code = mpld3.fig_to_html(ax,  **kw)
    # return html_code


def mpld3_server_start():
    """  Display mpld3 on server
    """
    # Windows specifc
    # if os.name == 'nt': os.system(f'start chrome "{dir_out}/embeds.html" ')
    # mpld3.show(fig=None, ip='127.0.0.1', port=8888, n_retries=50, local=True, open_browser=True, http_server=None, **kwargs)[source]
    mpld3.show()  # show the plot




############################################################################################################################
############################################################################################################################
def pd_plot_highcharts(df):
    """
    # Basic line plot
   chart = serialize(df, render_to="my-chart", title="My Chart")
   # Basic column plot
   chart = serialize(df, render_to="my-chart", title="Test", kind="bar")
   # Plot C on secondary axis
   chart = serialize(df, render_to="my-chart", title="Test", secondary_y = ["C"])
   # Plot on a 1000x700 div
   chart = serialize(df, render_to="my-chart", title="Test", figsize = (1000, 700))
    """
    import pandas_highcharts
    data = pandas_highcharts.serialize(
        df, render_to='my-chart', output_type='json')
    json_data_2 = "new Highcharts.StockChart(%s);" % pandas_highcharts.core.json_encode(
        data)

    html_code = """<div id="{chart_id}"</div>
      <script type="text/javascript">{data}</script>""".format(chart_id="new_brownian", data=json_data_2)
    return html_code



def pd_plot_scatter_highcharts(df0:pd.DataFrame, colx:str=None, coly:str=None, collabel: str=None,
                               colclass1: str=None, colclass2: str=None, colclass3: str=None, nsample=10000,
                               cfg:dict={}, mode='d3', save_img='', verbose=True, **kw)-> str:
    """ Plot Highcharts X=Y Scatter
    from utilmy.viz import vizhtml
    vizhtml.pd_plot_scatter_highcharts(df, colx:str=None, coly:str=None, collabel=None,
                               colclass1=None, colclass2=None, colclass3=None, nsample=10000,
                               cfg:dict={}, mode='d3', save_img=False,  verbose=True )
    """
    import matplotlib
    import matplotlib.pyplot as plt
    from box import Box
    from highcharts import Highchart

    cc = Box(cfg)
    cc.title      = cc.get('title',    'my scatter')
    cc.figsize    = cc.get('figsize', (640, 480) )   ### Dict type default values
    cc.colormap   = cc.get('colormap', 'brg')
    if verbose: print(cc['title'], cc['figsize'])

    nsample = min(nsample, len(df0))
    df   = df0.sample(nsample)

    colx      = 'x'      if colx is None else colx
    coly      = 'y'      if coly is None else coly
    collabel  = 'label'  if collabel is None else collabel    ### label per point
    colclass1 = 'class1' if colclass1 is None else colclass1  ### Color per point class1
    colclass2 = 'class2' if colclass2 is None else colclass2  ### Size per point class2
    colclass3 = 'class3' if colclass3 is None else colclass3  ### Marker per point


    #######################################################################################
    for ci in [ collabel, colclass1, colclass2 ] :
       if ci  not in df.columns : df[ci]  = ''  ### add missing
       df[ci]  = df[ci].fillna('')

    xx         = df[colx].values
    yy         = df[coly].values
    label_list = df[collabel].values

    ### Using Class 1 ---> Color
    color_list    = [ hash(str(x)) for x in df[colclass1].values     ]

    # Normalize the classes value over [0.0, 1.0]
    norm          = matplotlib.colors.Normalize(vmin=min(color_list), vmax=max(color_list))
    c_map         = plt.cm.get_cmap(cc.colormap)
    color_list    = [  matplotlib.colors.rgb2hex(c_map(norm(x))).upper() for x in color_list    ]


    ### Using Class 2  ---> Color
    n_size      = len(df[colclass2].unique())
    smin, smax  = 1.0, 15.0
    size_scheme = np.arange(smin, smax, (smax-smin)/n_size)
    n_colors    = len(size_scheme)
    size_list   = [  size_scheme[ hash(str( x)) % n_colors ] for x in df[colclass2].values     ]


    # Create chart object
    container_id = 'cid_' + str(np.random.randint(9999, 99999999))
    chart        = Highchart(renderTo=container_id)
    options      = {
      'chart':  {'width': cc.figsize[0], 'height': cc.figsize[1] },   'title': {'text': cc.title},
      'xAxis':  {'title': {'text': colx }},
      'yAxis':  {'title': {   'text': coly }},
      'legend': {'enabled': False },'tooltip': {'pointFormat': '{point.label}'}
    }

    chart.set_dict_options(options)

    # Plot each cluster with the correct size and color
    data = [{
        'x'     : float(xx[i]),
        'y'     : float(yy[i]),
        "label" : str(label_list[i]),
        "marker": { 'radius' : int(size_list[i]) },
        'color' : color_list[i]
        } for i in range(len(df))
    ]

    chart.add_data_set(data, 'scatter')
    chart.buildcontent()
    html_code = chart._htmlcontent.decode('utf-8')
    return html_code


def pd_plot_tseries_highcharts(df0,
                              coldate:str=None, date_format = None,
                              coly1:list =[],     coly2:list =[],
                              figsize:tuple =  None, title:str=None,
                              xlabel:str=None,  y1label:str=None, y2label:str=None,
                              cfg:dict={}, mode='d3', save_img="", verbose=True, **kw)-> str:
    '''  function to return highchart json cord for time_series.
    Docs::       
    
            df0         :        Panda dataframe on which you want to apply time_series.
            coldate     :        Column name for date.
            figsize     :        (10,7)
            date_format :        %m for moth , %d for day and %Y for Year.
            coly1=[]    :        Column name for y-axis one.
            coly2=[]    :        Column name for y-axis second.
            xlabel=None :        Label of x-axis.
            y1label=None:        Label for yaxis 1.
            y2label=None:        Label for yaxis 2.
    '''

    from highcharts import Highchart
    from box import Box
    cc = Box(cfg)
    import copy, datetime
    df = copy.deepcopy(df0)
    cc.coldate      = 'date'  if coldate is None else coldate
    cc.xlabel      = coldate if xlabel is None else xlabel
    cc.y1label   = "_".join(coly1)      if y1label is None else y1label
    cc.y2label   = "_".join(coly2)      if y2label is None else y2label
    cc.title        = cc.get('title',    str(y1label) + " vs " + str(coldate) ) if title is None else title
    cc.figsize      = cc.get('figsize', (800, 400) )    if figsize is None else figsize
    cc.subtitle     = cc.get('subtitle', '')
    cc.coly1    = coly1
    cc.coly2    = coly2
    #df[cc.coldate]     = pd.to_datetime(df[cc.coldate],format=date_format)    
    #df[cc.coldate] =  df[cc.coldate].dt.rng.strftime(date_format)
    ### Unix time in milit for highcharts
    import dateparser
    # vdate = [ 1000 * int( datetime.datetime.timestamp( datetime.datetime.strptime(t, date_format) ) ) for t in df[cc.coldate].values  ] 
    if date_format:
      vdate = [ 1000 * int( datetime.datetime.timestamp( datetime.datetime.strptime(str(t), date_format) ) ) for t in df[cc.coldate].values  ]
    else:
      vdate = [ 1000 * int( datetime.datetime.timestamp( dateparser.parse(str(t)) ) ) for t in df[cc.coldate].values  ]
    log(len(vdate), len(df))
    #########################################################
    container_id = 'cid_' + str(np.random.randint(9999, 99999999))
    H = Highchart(renderTo=container_id)
    options = {
      'chart':   {  "width": cc.figsize[0],
                    "height": cc.figsize[1],
                    'zoomType': 'xy'},
        'title': { 'text': cc.title},
        'subtitle': {  'text': cc.subtitle },
        'xAxis': [{'type': 'datetime', 'title': { 'text': cc.xlabel } }],
        'yAxis': [{'labels': {'style': {  'color': 'Highcharts.getOptions().colors[2]' } }, 
                   'title' : {'text': cc.y2label,
                   'style' : {   'color': 'Highcharts.getOptions().colors[2]' } }, 'opposite': True }, 
        {
            'gridLineWidth': 0,
            'title':  {'text': cc.y1label, 'style': { 'color': 'Highcharts.getOptions().colors[0]'}},
            'labels': {'style': { 'color': 'Highcharts.getOptions().colors[0]'} }

        }],

        'tooltip': { 'shared': True,    },
        'legend': {
            'layout': 'vertical', 'align': 'left', 'x': 80, 'verticalAlign': 'top', 'y': 55,
            'floating': True,
            'backgroundColor': "(Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'"
        },
    }
    H.set_dict_options(options)

    # vdate = df[cc.coldate].values
    for col_name in cc.coly1:
#       df[col_name].fillna(0, inplace = True)
      df.loc[:,col_name] = df[col_name].fillna(0)
      data = [[ vdate[i] , to_float(df[col_name].iloc[i] ) ] for i in range(df.shape[0])]
      H.add_data_set(data, 'spline', col_name,yAxis=1)

    for col_name in cc.coly2:
#       df[col_name].fillna(0, inplace = True)
      df.loc[:,col_name] = df[col_name].fillna(0)
      data = [[ vdate[i] , to_float(df[col_name].iloc[i] )] for i in range(df.shape[0])]
      H.add_data_set(data, 'spline', col_name, yAxis=0, )

    ##################################################################
    H.buildcontent()
    html_code = H._htmlcontent.decode('utf-8')
    return html_code



def pd_plot_histogram_highcharts(df:pd.DataFrame, colname:str=None,
                              binsNumber=None, binWidth=None,color:str='#7CB5EC',
                              title:str="", xaxis_label:str= "x-axis", yaxis_label:str="y-axis",
                              cfg:dict={}, mode='d3', save_img="",
                              show=False, verbose=True, **kw):

    ''' function to return highchart json code for histogram.
    Docs::

        df             :        panda dataframe on which you want to apply histogram.
        colname=None   :        Column name from dataframe in which histogram will apply.
        binsNumber=None:        Number of bin in bistogram.
        binWidth=None  :        Width of each bin in histogram.
        color=None     :        Color of histogram.
        title          :        Title of histogram
        xaxis_label    :        Label for x-axis
        yaxis_label    :        Label for y-axis
        cfg            :        Configuretion dictionary for highcharts.
        save_img=""    :        Path to save image.
        show=False     :        Show image.
        verbose=True   :        Verbose mode.

    '''
    cc = Box(cfg)
    cc.title        = cc.get('title',    "My Title" ) if title is None else title
    cc.xaxis_label  = xaxis_label if xaxis_label else "x-axis"
    cc.yaxis_label  = yaxis_label if yaxis_label else "y-axis"

    container_id = 'cid_' + str(np.random.randint(9999, 99999999))
#     data         = df[colname].values.tolist()
#     df[colname] = df[colname].fillna(0)
#     df[colname].fillna(0, inplace = True)
    df.loc[:,colname] = df[colname].fillna(0)

    data = [ to_float(t) for t in df[colname].values  ]  
      
    code_html_start = f"""
         <script src="https://code.highcharts.com/6/modules/histogram-bellcurve.js"></script>
             <div id="{container_id}">Loading</div>
         <script>
    """

    data_code = """
     var data = {data}
     """.format(data = data)

    title  = """{ text:'""" + cc.title +"""' }"""

    xAxis = """[{
                title: { text:'""" + cc.xaxis_label + """'},
                alignTicks: false, opposite: false
            }]"""

    yAxis = """[{
                title: { text:'""" + cc.yaxis_label + """'}, opposite: false
            }] """

    append_series1 = """[{
            name: 'Histogram', type: 'histogram', baseSeries: 's1',"""

    if binsNumber is not None:
      append_series1 += """ binsNumber:{binsNumber},  """.format(binsNumber = binsNumber)

    if binWidth is not None:
      append_series1 += """ binWidth:{binWidth},""".format(binWidth = binWidth)

    append_series2 =  """}, {
            name: ' ', type: 'scatter', data: data, visible:false, id: 's1', marker: {  radius: 0}
        }] """

    append_series = append_series1 + append_series2

    js_code = """Highcharts.chart('"""+container_id+"""', {
        colors:""" + "['"+color+"""'],
        title:""" +  title+""",
        xAxis:""" +  xAxis+""",
        yAxis:""" +  yAxis+""",
        series: """+append_series+"""
    });
    </script>"""

    html_code = data_code + js_code

    # if show :
    html_code = code_html_start + html_code

    # print(html_code)
    return html_code


def html_show_chart_highchart(html_code, verbose=True):
    """
    Function to display highcharts graph
    Docs::

            html_code   :        html code of highcharts graph
            verbose=True:        if True, print html code
    """

    # Function to display highcharts graph
    from highcharts import Highchart
    from IPython.core.display import display, HTML
    hc = Highchart()
    hc.buildhtmlheader()
    html_code = hc.htmlheader + html_code
    if verbose: print(html_code)
    display(HTML(html_code))



def html_show(html_code, verbose=1):
    # Function to display HTML
    """
    Function to display HTML
    Docs::

            html_code   :        html code of HTML
            verbose=True:        if True, print html code
    """
    from IPython.core.display import display, HTML
    display(HTML( html_code))



############################################################################################################################
############################################################################################################################
def images_to_html(dir_input="*.png",  title="", verbose=False):
    """
    Function to convert images to html code
    Docs::

            dir_input="*.png":        directory of images
            title=""         :        title of html code
            verbose=False    :        if True, print html code
    """
    #     images_to_html( model_path + "/graph_shop_17_past/*.png" , model_path + "shop_17.html" )
    import matplotlib.pyplot as plt
    import base64, glob
    from io import BytesIO
    html = ""
    flist = glob.glob(dir_input)
    flist.sorted()
    for fp in flist:
        if verbose:
            print(fp, end=",")
        with open(fp, mode="rb") as fp2:
            tmpfile = fp2.read()
        encoded = base64.b64encode(tmpfile) .decode('utf-8')
        html = html + \
            f'<p><img src=\'data:image/png;base64,{encoded}\'> </p>\n'

    return html


def colormap_get_names():
  """Function to get list of colormap names with plot.



  """
  import matplotlib.pyplot as plt
  cmaps = {}
  cmaps['uniform_sequential'] = [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis']
  cmaps['sequential'] = [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
  cmaps['sequential_2'] = [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']
  cmaps['diverging'] = [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']
  cmaps['cyclic'] = ['twilight', 'twilight_shifted', 'hsv']
  cmaps['qualitative'] = ['Pastel1', 'Pastel2', 'Paired', 'Accent',
                        'Dark2', 'Set1', 'Set2', 'Set3',
                        'tab10', 'tab20', 'tab20b', 'tab20c']
  gradient = np.linspace(0, 1, 256)
  gradient = np.vstack((gradient, gradient))


  def plot_color_gradients(cmap_category, cmap_list):
      # Create figure and adjust figure height to number of colormaps
      nrows = len(cmap_list)
      figh = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22
      fig, axs = plt.subplots(nrows=nrows + 1, figsize=(6.4, figh))
      fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,
                          left=0.2, right=0.99)
      axs[0].set_title(cmap_category + ' colormaps', fontsize=14)

      for ax, name in zip(axs, cmap_list):
          ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(name))
          ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10,
                  transform=ax.transAxes)

      # Turn off *all* ticks & spines, not just the ones with colormaps.
      for ax in axs:
          ax.set_axis_off()


  for cmap_category, cmap_list in cmaps.items():
      plot_color_gradients(cmap_category, cmap_list)

  plt.show()


############################################################################################################################
############################################################################################################################
def pd_plot_network(df:pd.DataFrame, cola: str='col_node1', 
                    colb: str='col_node2', coledge: str='col_edge',
                    colweight: str="weight",html_code:bool = True):
    """  Function to plot network https://pyviz.org/tools.html
    Docs::

            df                :        dataframe with nodes and edges
            cola='col_node1'  :        column name of node1
            colb='col_node2'  :        column name of node2
            coledge='col_edge':        column name of edge
            colweight="weight":        column name of weight
            html_code=True    :        if True, return html code
    """

    def convert_to_networkx(df:pd.DataFrame, cola: str="", colb: str="", colweight: str=None):
        """
        Convert a panadas dataframe into a networkx graph
        and return a networkx graph
        Docs::

                df                :        dataframe with nodes and edges
        """
        import networkx as nx
        import pandas as pd
        g = nx.Graph()
        for index, row in df.iterrows():
            g.add_edge(row[cola], row[colb], weight=row[colweight],)

        nx.draw(g, with_labels=True)
        return g


    def draw_graph(networkx_graph, notebook:bool =False, output_filename='graph.html',
                   show_buttons:bool =True, only_physics_buttons:bool =False,html_code:bool  = True):
        """  This function accepts a networkx graph object, converts it to a pyvis network object preserving
        its node and edge attributes,
        and both returns and saves a dynamic network visualization.
        Valid node attributes include:
            "size", "value", "title", "x", "y", "label", "color".
            (For more info: https://pyvis.readthedocs.io/en/latest/documentation.html#pyvis.network.Network.add_node)

        Docs::

                networkx_graph: The graph to convert and display
                notebook: Display in Jupyter?
                output_filename: Where to save the converted network
                show_buttons: Show buttons in saved version of network?
                only_physics_buttons: Show only buttons controlling physics of network?
        """
        from pyvis import network as net
        import re
        # make a pyvis network
        pyvis_graph = net.Network(notebook=notebook)

        # for each node and its attributes in the networkx graph
        for node, node_attrs in networkx_graph.nodes(data=True):
            pyvis_graph.add_node(str(node), **node_attrs)

        # for each edge and its attributes in the networkx graph
        for source, target, edge_attrs in networkx_graph.edges(data=True):
            # if value/width not specified directly, and weight is specified, set 'value' to 'weight'
            if not 'value' in edge_attrs and not 'width' in edge_attrs and 'weight' in edge_attrs:
                # place at key 'value' the weight of the edge
                edge_attrs['value'] = edge_attrs['weight']
            # add the edge
            pyvis_graph.add_edge(str(source), str(target), **edge_attrs)

        # turn buttons on
        if show_buttons:
            if only_physics_buttons:
                pyvis_graph.show_buttons(filter_=['physics'])
            else:
                pyvis_graph.show_buttons()

        # return and also save
        pyvis_graph.show(output_filename)
        if html_code:

          def extract_text(tag: str,content: str)-> str:
            reg_str = "<" + tag + ">\s*((?:.|\n)*?)</" + tag + ">"
            extracted = re.findall(reg_str, content)[0]
            return extracted
          with open(output_filename) as f:
            content = f.read()
            head = extract_text('head',content)
            body = extract_text('body',content)
            return head, body
    networkx_graph = convert_to_networkx(df, cola, colb, colweight=colweight)
    head, body = draw_graph(networkx_graph, notebook=False, output_filename='graph.html',
               show_buttons=True, only_physics_buttons=False,html_code = True)
    return head, body








def pd_plot_network_cyto(df:pd.DataFrame, cola: str='col_node1',
                    colb: str='col_node2', coledge: str='col_edge',
                    colweight: str="weight",html_code:bool = True):
    """  Function to plot network using cytoscape
    Docs::

        -- Like regular pd_plot_network, just call cyto instead)
            doc.h1(" plot network")
            df = pd.DataFrame({ 'from':['A', 'B', 'C','A'], 'to':['D', 'A', 'E','C'], 'weight':[1, 2, 1,5]})
            doc.pd_plot_network_cyto(df, cola='from', colb='to', coledge='weight')
            doc.save('test5.html')
            doc.open_browser()


        df                :        dataframe['from', 'to', 'edge    ]
        cola='col_node1'  :        column name of node1
        colb='col_node2'  :        column name of node2
        coledge='col_edge':        column name of edge
        colweight="weight":        column name of weight
        html_code=True    :        if True, return html code

    """
    from box import Box
    args = Box({})

    node_color  = "#6200EE"
    label_color = "#03DAC6"
    edge_color  = "#3700B3"


    data = ""
    node_ids = set()

    for ii, edge in df.iterrows():
        node_ids.add(edge[cola])
        node_ids.add(edge[colb])

    for node_id in node_ids:
        data += f"""{{ data: {{ id:     '{node_id}' }} }},\n"""
    
    for ii, node in df.iterrows():
        data += f"""{{ data: {{ id:     '{node[cola]}->{node[colb]}', 
                                source: '{node[cola]}', 
                                target: '{node[colb]}' }} }},\n"""


    head = f"""
         <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.22.1/cytoscape.min.js"></script></head>                
         <style>
            #cy {{
                width: 90%;
                height: 80%;
                position: relative;
                top: 10px;
                left: 0px;
            }}
         </style>  
    """

    body =  f"""        
        <div id=\"cy\"></div>
        <script>
            var cy = cytoscape({{
    
            container: document.getElementById('cy'),
    
            elements: [{data}],
            style: [
                {{\nselector: 'node',
            style: {{label: 'data(id)',
            'background-color': '{node_color}',
            'color': '{label_color}'
    
            }}}},
            {{
            selector: 'edge',
            style: {{'line-color': '{edge_color}'}}\n
            }}
            ]
            }});
        </script>
        """
    return head, body







###################################################################################################
######### JScript #################################################################################
js_code = Box({})  # List of javascript code
js_code.js_hidden = """<script>
var x = document.getElementById('hidden_section_id');
x.onclick = function() {
    if (x.style.display == 'none') {
        x.style.display = 'block';
    } else {
        x.style.display = 'none';
    }
}
</script>
"""




###################################################################################################
###################################################################################################
def help_get_codesource(func):
    """ Extract code source from func name
    Docs::

            func:        function to extract code source from
    """
    import inspect
    try:
        lines_to_skip = len(func.__doc__.split('\n'))
    except AttributeError:
        lines_to_skip = 0
    lines = inspect.getsourcelines(func)[0]
    return ''.join( lines[lines_to_skip+1:] )


def to_float(x):
    """Convert x to float if possible
    Docs::

            x:        object to convert to float
    """
    try: return float(x)
    except : return 0


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()
    # test2()