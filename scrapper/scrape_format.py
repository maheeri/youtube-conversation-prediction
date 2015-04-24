import re
#Regex solution:
scrapped_filename = "" #input
my_file = open(scrapped_filename)
content = my_file.read()
data_str = re.findall( r"<graph_data><!\[CDATA(.*)]></graph_data></root>", content)[0]
data_str = re.sub('false', 'False', data_str)
data_str = re.sub('true', 'True', data_str)
data = eval(data_str)

views = data[0]['views']['cumulative']['data']
max_views = data[0]['views']['cumulative']['opt']['vAxis']['maxValue']