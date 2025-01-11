# Introduction
## Install package
```shell
pip install api_cat
```
##  ContactOut Usage:
```python
api_token = "xxxxxxxxxxxxx"  # API Token

api = ContactOutAPI(api_token)

# Get Usage Status
api.usage_status()

# Search By Email
email = "xxxx@gmail.com"
print("Search LinkedIn URL by Email:")
api.search_linkedin_url_by_email(email)

print("Search LinkedIn Profile by Email:")
api.search_linkedin_profile_by_email(email)

profile_url = "https://www.linkedin.com/in/chao-zhang-08a216a7/"

# Search By linkedin_url
print("Search Profile by LinkedIn URL:")
api.search_profile_by_linkedin_url(profile_url)

print("Search Email by Linkedin URL:")
api.search_email_by_linkedin_url(profile_url)


# Search Filter
api.search_filter(name='Hanwang Zhang')


```



## 



