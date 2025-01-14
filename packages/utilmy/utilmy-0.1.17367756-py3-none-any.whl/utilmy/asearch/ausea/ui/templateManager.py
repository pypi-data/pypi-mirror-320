"""
   Test

      python ui/templateManager.py test1
      python ui/templateManager.py json_to_html


      


"""
import re
import json
from jinja2 import Template, TemplateError
from utilmy import log, date_now
import uuid


#################################################################################
def test_all():
    tes1()


def test1():
    pass


#################################################################################
def open_read(fpath):
    try:
        with open(fpath, mode='r') as fp:
            txt = fp.read().strip()
        return txt
    except Exception as e:
        log(e)
        return ""


def split_text(text):
    sentences = re.split(r'(?<=\.)\s+(?=[A-Z])', text)
    return sentences


def generate_random_id():
    # Generate a random ID using UUID
    return f"data-table-{uuid.uuid4().hex[:8]}"


def json_to_html(fdata="ui/static/answers/overview/data.json", ftemplate="ui/static/answers/overview/html.html"):
    if isinstance(ftemplate, str):
        template_str = open_read(ftemplate)
    else:
        template_str = ftemplate

    if isinstance(fdata, dict):
        data_dict = fdata
    else:
        try:
            json_content = open_read(fdata)
            data_dict = json.loads(json_content)
        except json.JSONDecodeError as e:
            log(f"Invalid JSON format in file {fdata}: {e}")
            raise ValueError(f"Invalid JSON format in file {fdata}: {e}")

    try:
        template = Template(template_str)
        html_output = template.render(data_dict['html_tags'],
                                      split_text=split_text,
                                      generate_random_id=generate_random_id)
        return html_output
    except TemplateError as e:
        log(f"Error rendering template: {e}")
        raise TemplateError(f"Error rendering template: {e}")


########################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()
