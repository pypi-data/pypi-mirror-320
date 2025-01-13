import os
import glob
import zipfile

from lxml import etree
import requests

from sample_config import PAPERLESS_INSTANCE, PAPERLESS_TOKEN

headers = {
	"Authorization": f"Token {PAPERLESS_TOKEN}"
}

def map_custom_fields(dic):
	mp = {
		"type": 1,
		"reg_num": 2,
		"reg_type": 3,
		"org_name": 4,
		"org_place": 5,
	}
	return { mp[key]: val for key, val in dic.items() }

for folder in glob.glob("./download-*"):
	org = {"type": "registerportal"}
	print(folder)

	for xml_file in glob.glob(folder + "/*.xml"):
		ns={'t': 'http://www.xjustiz.de'}
		print(xml_file)
		ctxt = etree.parse(xml_file)
		reg_num = ctxt.xpath("//t:aktenzeichen.strukturiert//code", namespaces=ns)
		reg_type = ctxt.xpath("//t:aktenzeichen.strukturiert//t:laufendeNummer", namespaces=ns)
		# for person in ctxt.xpathEval("//tns:natuerlichePerson"):
		# 	person_first = person.xpathEval("//tns:natuerlichePerson//tns:vorname")
		# 	person_first = person.xpathEval("//tns:natuerlichePerson//tns:nachname")
		# 	person_born = person.pathEval("//tns:geburtsdatum")
		# 	person_place = person.pathEval("//tns:ort")

		org_name = ctxt.xpath("//t:rechtstraeger//t:bezeichnung//t:bezeichnung.aktuell", namespaces=ns)
		org_place = ctxt.xpath("//t:rechtstraeger//t:sitz//t:ort", namespaces=ns)

		def txt(lis):
			strs = [item.text for item in lis]
			return ''.join(strs)

		org["reg_num"] = txt(reg_num)
		org["reg_type"] = txt(reg_type)
		org["org_name"] = txt(org_name)
		org["org_place"] = txt(org_place)

		print(org)

	for zip_file in glob.glob(folder + "/*.zip"):
		zf = zipfile.ZipFile(zip_file)
		zf.extractall(path=folder)

	for pdf_file in [
						x
    					for xs in [glob.glob(folder + ext) for ext in ["/*.pdf", "/*.tiff"]]
    					for x in xs
    				]:

		files = {'document': open(pdf_file,'rb')}

		fields = [
			("title", os.path.basename(pdf_file)),
		] + [ 
			("custom_fields", { key: val }) for key, val in map_custom_fields(org).items()
		]
		print(fields)
		r = requests.post(f"https://{PAPERLESS_INSTANCE}/api/documents/post_document/", files=files, headers=headers, data=fields)
		print(r.status_code)
		print(r.text)
