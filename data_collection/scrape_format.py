from __future__ import division
import json
import datetime
from dateutil.parser import parse
import os

def get_date(target_views, path, vid_id):
    """
    =Inputs=
    target_views : int
        The desired number of views to return a date at
    path: string
        The location of the .scrape files
    vid_id: string
        The video id of the video to get the date via scraped json
    =Outputs=
    Case 1:
        error: float
            % error of approxmation
        views returned for: int
            # of views returned for
        approx_date: datetime (day specific)
            the day where said number of views were achieved
    Case 2:
        flag: None
            Check if the first arg is none, this means that the input does not 
            reach above the target_views
        views returned for: int
            # of views returned for
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
    #read scrape from json
    scrape = json.load(open(path+vid_id+'.scrape'))
    #get data
    views_list   = scrape['data']
    ret_date_str = scrape['ret_date']
    pub_date_str = scrape['pub_date']
    #convert dates to datetime
    ret_date     = parse(ret_date_str)
    pub_date     = parse(pub_date_str)

    #get neighboring views and idx
    views_idxs = get_views_idxs(target_views, views_list)
    if views_idxs == None:
        print "Video does not have", target_views, "views"
        return (None, views_list[-1])
    
    #get closest views and idx
    sorted_view_idxs = sorted([(abs(views_list[views_idx] - target_views), views_idx )for views_idx in views_idxs])
    distance, cloest_view_idx = sorted_view_idxs[0]
    
    #get approximation error
    error = (distance/target_views)
    
    #get approximated date
    date_approx_ratio = cloest_view_idx/len(views_list)
    days_diff = (ret_date - pub_date).days
    days_from_pub = days_diff * date_approx_ratio
    date_target = pub_date + datetime.timedelta(days=days_from_pub)
    
    
    return (error, views_list[cloest_view_idx], date_target)
    
if __name__ == "__main__":
    os.chdir(os.path.join(os.pardir, 'data')) #go into data folder
    res = get_date(10000, "scraped/", 'wmIodQq5Erk')
    print res