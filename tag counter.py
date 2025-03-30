import requests
import operator
import json
from decimal import *
import os

# target_list is a list of doujin ids
def count(target_list):
    not_found = []
    tags_map = {}
    tag_counts = {}
    yuri = []
    yaoi = []
    doujin_count = 0
    metadata = []
    # the cache file won't exist the first time you run this so we must go ask the API
    if os.path.exists("doujin_metadata_cache.json"):
        try:
            metadata_file = open("doujin_metadata_cache.json", "r")
        except:
            print("this shouldn't really happen, maybe try running again?")
        metastring = metadata_file.readlines()
        response_list = json.loads(metastring[0]) # retrieves the json responses from the cache file
        # same as the API path except we use the cached json
        for i in response_list:
            request_body = i
            doujin_count += 1
            tag_list = request_body["tags"]
            for j in tag_list:
                if j["name"] in tags_map:
                    tags_map[j["name"]] += 1
                else:
                    if j["type"] == "tag":
                        tags_map[j["name"]] = 1
                        tag_counts[j["name"]] = j["count"]
                if j["name"] == "yuri":
                    yuri.append([request_body["id"], request_body["title"]["pretty"]])
                    #print(f"YURI FOUND!!! | {request_body["title"]["pretty"]}")
                elif j["name"] == "yaoi":
                    yaoi.append([request_body["id"], request_body["title"]["pretty"]])
                    #print(f"YAOI SPOTTED!!!! | {request_body["title"]["pretty"]}")
                        
            print(f"{i.strip()} mapped {target_list.index(i) + 1}/{len(target_list)}")
        return tags_map, not_found, tag_counts, yuri, yaoi, doujin_count
    else:
        # This is single-threaded IO-bound python so this should take a really long time to finish
        # rewrite this in asyncio if you want
        for i in target_list:
            request = requests.get(f"https://nhentai.net/api/gallery/{i.strip()}")
            request_body = request.json()
            # check whether the API was happy about the request
            if "error" not in request_body:
                metadata.append(request_body) # save result to cache so we don't have to ask the API again later
                doujin_count += 1
                tag_list = request_body["tags"]
                for j in tag_list:
                    if j["name"] in tags_map:
                        tags_map[j["name"]] += 1 # if the tag has been seen before, add 1 to the count
                    else:
                        if j["type"] == "tag": # there are other tag types we're not really interested in like artist and group
                            tags_map[j["name"]] = 1 # if the tag is new, create a new dictionary key for it and init as 1
                            tag_counts[j["name"]] = j["count"] # also keep the sitewide tag count for later
                    if j["name"] == "yuri":
                        yuri.append([request_body["id"], request_body["title"]["pretty"]]) # if this is a yuri doujin, keep the id for later
                        #print(f"YURI FOUND!!! | {request_body["title"]["pretty"]}") # you can uncomment this line if the whimsy levels require it
                    elif j["name"] == "yaoi":
                        yaoi.append([request_body["id"], request_body["title"]["pretty"]]) # if this is a yaoi doujin, keep the id for later
                        #print(f"YAOI SPOTTED!!!! | {request_body["title"]["pretty"]}") # same as the other line
                        
                print(f"{i.strip()} mapped {target_list.index(i) + 1}/{len(target_list)}") # update the user so they know progress is happening
                
            else:
                # we're mainly interested in 404 errors so we can populate the missing doujins list
                if request_body["error"] == "does not exist":
                    print(f"{i.strip()} does not exist")
                    not_found.append(i.strip())
                else:
                    # this path exists just in case some other unexpected error gets returned by the API
                    # in that case, you should read the error (maybe a rate limit of some kind?) and decide whether to proceed or abort
                    print(f"{i.strip()} error: {request_body["error"]}")
                    aux = input("input needed (abort?) ")
                    if aux.casefold() == "abort" or aux.casefold() == "y" or aux.casefold() == "yes": #if the input doesn't match we'll keep going
                        # save whatever was already acquired to disk
                        temp_metadata = json.dumps(metadata)
                        json_file = open("doujin_metadata_cache.json", "w")
                        json_file.write(temp_metadata)
                        json_file.close()
                        # get back to main
                        return tags_map, not_found, tag_counts, yuri, yaoi, doujin_count
        # save the results to disk so we don't have to ask the API next time
        temp_metadata = json.dumps(metadata)
        json_file = open("doujin_metadata_cache.json", "w")
        json_file.write(temp_metadata)
        json_file.close()
        return tags_map, not_found, tag_counts, yuri, yaoi, doujin_count
    
def main():
    if not os.path.exists("numbers.txt"):
        print("doujin ids file not found")
        raise RuntimeError("doujin ids file not found")
    
    f = open("numbers.txt", "r") # this is the file you need to provide, with 1 doujin id per line
    
    # create output files
    output0 = open("tag_map_measure_0.txt", "w")
    output1 = open("tag_map_measure_1.txt", "w")
    output2 = open("tag_map_measure_2.txt", "w")
    nf = open("not_found.txt", "w")
    yu = open("yuri.txt", "w")
    ya = open("yaoi.txt", "w")
    
    targets = f.readlines() # get the list of ids
    results, missing, tag_counts, yuri, yaoi, doujin_count = count(targets) # here we call the API, as described above
    
    results0 = {}
    results1 = {}
    results2 = {}
    #const_total_doujin = 529343
    print("processing")
    
    # compute some sums for usage in some of the measures
    # we could probably list comprehension this but eh
    obs_tag_sum = 0
    for i in results:
        obs_tag_sum += results[i]
    real_tag_sum = 0
    for i in tag_counts:
        real_tag_sum += tag_counts[i]
        
    for i in results: # feel free to change measure formulas or whatever
        # this is just the tag count
        results0[i] = results[i]
        # we use Decimal because all my homies hate float
        # tag_counts[i] / (real_tag_sum/obs_tag_sum) gives us the expected value for that tag in the observed dataset, according to the sitewide dataset
        # e.g. for a 50 tags sitewide dataset and a 10 tags observed dataset, we expect to see a 5 count tag 1 time
        # results[i] / the expected value tells us how different the actual value is from the expectations
        # e.g. if the example tag is seen 3 times we return that it is 3.0 times the expected value (1)
        results1[i] = Decimal(results[i]) / (Decimal(tag_counts[i]) / (Decimal(real_tag_sum) / Decimal(obs_tag_sum)))
        # sitewide tag counts if you want to look at them and compute outliers and such
        results2[i] = tag_counts[i]
    
    # dicts actually don't have an order but we sort them by values anyway
    # also we need to reverse the sort to get the highest values at the top
    # there are many better ways to do this
    sorted_results0 = sorted(results0.items(), key=operator.itemgetter(1))
    sorted_results1 = sorted(results1.items(), key=operator.itemgetter(1))
    sorted_results2 = sorted(results2.items(), key=operator.itemgetter(1))
    sorted_results0.reverse()
    sorted_results1.reverse()
    sorted_results2.reverse()
    
    # this input file holds a one-per-line (manually curated) list of all the tags that aren't really tags
    # this includes stuff like "rough translation", "incomplete", and "out of order"
    # but should also include artist names that are mistakenly included as a tag, since that really messes up the expected value computations
    # you should also look at your results and add artist names that show up there to this file, before running this script again
    # (they're easy to spot because the scores will be really high but when you look them up on nhentai they match the artist on the title of the doujin, and also there'll be like 1 doujin with that tag in the entire site)
    ban_file = open("not_real_tags.txt", "r")
    ban_list = ban_file.readlines()
    ban_file.close()
    for i in range(0, len(ban_list)):
        ban_list[i] = ban_list[i].strip()
    
    # any tags with really low sitewide count will throw off the expected values so you can use this to ignore them
    tag_count_cutoff = 15 # you can change the minimum value or set it to 0 to include everything
    
    # here we write to disk in a reasonably human-readable way
    for i in sorted_results0:
        if i[0] not in ban_list and tag_counts[i[0]] > tag_count_cutoff:
            output0.write(f"{i[0]} | {str(round(i[1], 2))}\n")
    for i in sorted_results1:
        if i[0] not in ban_list and tag_counts[i[0]] > tag_count_cutoff:
            output1.write(f"{i[0]} | {str(round(i[1], 2))}\n")
    for i in sorted_results2:
        output2.write(f"{i[0]} | {str(round(i[1], 2))}\n")
        
    for i in yuri:
        yu.write(f"https://nhentai.net/g/{i[0]} | {i[1]}\n")
    for i in yaoi:
        ya.write(f"{i[0]} | {i[1]}\n")
    for i in missing:
        nf.write(f"{i}\n")
        
    f.close()
    output0.close()
    output1.close()
    output2.close()
    nf.close()
    yu.close()
    ya.close()
    
    print(f"done | {doujin_count} doujins processed")
    
# run main
if __name__ == "__main__":
    main()
