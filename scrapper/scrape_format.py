from __future__ import division
import re
import dateutil
import datetime

def get_date(target_views, pub_date, scrapped_filename, scrapped_path="scraped/"):
    """
    =Inputs=
    target_views : int
        The desired number of views to return a date at
    pub_date: datetime (day specific )
        The approixmated date where the video had that many views
    =Outputs=
    error: float
        % error of approxmation
    approx_date: datetime (day specific)
        the day where said number of views were achieved
    """
    def get_views_idxs(target_views, views_list):
        for idx,views in enumerate(views_list):
            if views == target_views:
                return [idx]
            if views > target_views:
                if (idx > 0):
                    return [idx-1,idx] #average of previous and current
                else:
                    return [idx]
        return None
    #read scrape via regex
    my_file = open(scrapped_path+scrapped_filename+'.scrape')
    content = my_file.read()

    #get data
    data_str = re.findall(r"<graph_data><!\[CDATA(.*)]></graph_data>", content)[0]
    data_str = re.sub('false', 'False', data_str)
    data_str = re.sub('true', 'True', data_str)
    data = eval(data_str)
    views_list = data[0]['views']['cumulative']['data']

    #get date
    ret_date_str = re.findall(r"%TIME_START%(.*)%TIME_END%", content)[0]
    ret_date = dateutil.parser.parse(ret_date_str)


    #get neighboring views and idx
    views_idxs = get_views_idxs(target_views, views_list)
    if views_idxs == None:
        return None
    
    #get closest views and idx
    sorted_view_idxs = sorted([(abs(views_list[views_idx] - target_views), views_idx )for views_idx in views_idxs])
    distance, cloest_view_idx = sorted_view_idxs[0]
    
    #get approximation error
    error = (distance/target_views)
    
    #get approximated date
    date_approx_ratio = cloest_view_idx/len(views_list)
    days_diff = (ret_date - pub_date).days
    days_from_pub = round(days_diff * date_approx_ratio)    
    date_target = pub_date + datetime.timedelta(days=days_from_pub)
    
    
    return (error, date_target)

if __name__ == "__main__":
    pub_date_str = 'Sep 25, 2014'
    pub_date = dateutil.parser.parse(pub_date_str)
    get_date(100000, pub_date, 'o6mA6y6KMmA')