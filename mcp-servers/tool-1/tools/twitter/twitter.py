""" https://developer.x.com/en/docs/x-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-list
"""
from typing import List

from datetime import datetime
import os
import time
import json
import requests
import logging
import random
from urllib import request
from urllib.request import Request, urlopen
from urllib.parse import quote
from dotenv import load_dotenv
from typing import Annotated
from pydantic import Field
from fake_useragent import UserAgent

from tools.twitter.tweet_schema import TweetSchema, UserSchema
import timeout_decorator


load_dotenv()

class PageContentGetter:
    def __init__(self, curl_dir, proxy=None, from_json=True):
        """
        Initialize PageContentGetter with optional headers and proxy
        
        Args:
            headers (dict, optional): Headers to use for requests. Defaults to None.
            proxy (dict, optional): Proxy configuration. Defaults to None.
            opener (urllib.OpenerDirector, optional): Custom opener. Defaults to global opener.
        """
        try:
            self.curl_dir = curl_dir
            self.ua = UserAgent()
            self.proxy = proxy
            self.from_json = from_json
            opener = self.get_opener(from_json=from_json)
            self.opener = opener
            request.install_opener(self.opener)
        except Exception as e:
            logging.error(f"Error initializing PageContentGetter: {str(e)}")
            raise

    def get_opener(self, from_json: bool = True):
        if not from_json:
            curl_name = random.choice([file for file in os.listdir(self.curl_dir) if file.endswith('.txt')])
            curl_path = os.path.join(self.curl_dir, curl_name)
            with open(curl_path, 'r') as f:
                curl = f.read()
            headers = self.get_headers_from_curl(curl)
        else:
            group_headers = self.get_headers_from_json(os.path.join(self.curl_dir, 'mkt_dev01_access_headers.json'))
            if group_headers:
                headers = random.choice(group_headers)
            else:
                headers = []

        if self.proxy:
            proxy_handler = request.ProxyHandler(self.proxy)
            opener = request.build_opener(proxy_handler)
        else:
            opener = request.build_opener()
        if headers:
            opener.addheaders = headers
        return opener

    def rotate_opener(self):
        self.opener = self.get_opener(from_json=self.from_json)
        request.install_opener(self.opener)

    def get_headers_from_json(self, json_file):
        with open(json_file, 'r') as f:
            headers = json.load(f)
        new_headers = []
        for header in headers:
            header_json = json.loads(header['headers'])
            header = []
            for key, value in header_json.items():
                header.append((key.strip(), value.strip()))
            new_headers.append(header)
        return new_headers

    def get_headers_from_curl(self, curl_command):
        headers = []
        lines = curl_command.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-H'):
                # Remove -H and strip quotes
                header = line[3:].strip("' \\")
                if ':' in header:
                    key, value = header.split(':', 1)
                    if key.strip() == 'user-agent':
                        value = self.ua.random
                    headers.append((key.strip(), value.strip()))
        return headers

    def get_content(self, url, head=None):
        """
        Get page content using configured opener
        
        Args:
            url (str): URL to fetch content from
            head (dict, optional): Additional headers. Defaults to None.
            
        Returns:
            urllib.response.addinfourl: Response from urlopen
        """
        try:
            request.install_opener(self.opener)
            req = Request(url)
            if head:
                for k, v in head.items():
                    req.add_header(k, v)
            return urlopen(req)
        except Exception as e:
            logging.error(f"Error getting content from {url}: {str(e)}")
            raise

    def get_json(self, url, head=None):
        """
        Get JSON response from URL
        
        Args:
            url (str): URL to fetch JSON from
            head (dict, optional): Additional headers. Defaults to None.
            
        Returns:
            dict: Parsed JSON response
        """
        try:
            self.rotate_opener()
            response = self.get_content(url, head)
            return json.loads(response.read())
        except Exception as e:
            logging.error(f"Error getting JSON from {url}: {str(e)}")
            raise


# proxies = {
#     'http': 'http://localhost:9999',
# }

absolution_path = os.path.abspath(__file__)
curls_dir = os.path.join(os.path.dirname(absolution_path), 'curls', 'twitter')
twitter_getter = PageContentGetter(curls_dir)


def get_friends(
    user_id: Annotated[str, Field(default='', description="Twitter user ID")],
    user_name: Annotated[str, Field(default='', description="Twitter username")],
    cursor: Annotated[str, Field(default='',description="Pagination cursor for fetching next page")],
    count: Annotated[int, Field(default=20, description="Number of friends to retrieve")]
) -> list:
    url = 'https://api.x.com/1.1/friends/ids.json?'
    if user_id and user_id.strip():
        url += f'user_id={user_id}'
    elif user_name and user_name.strip():
        url += f'screen_name={user_name}'
    if cursor and cursor.strip():
        url += f'&cursor={cursor}'
    if count:
        url += f'&count={count}'
    print(url)
    result = twitter_getter.get_json(url)
    if result:
        try:
            return result
        except Exception:
            import traceback
            traceback.print_exc()
            return None
    return None


def get_tweet(entry):
    tweet_id = entry['entryId'].split('-')[-1]
    result_entry = entry['content']['itemContent']['tweet_results']['result']['legacy']
    content = result_entry['full_text']
    user_id = result_entry['user_id_str']
    user_name = entry['content']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']['screen_name']

    view_count = entry['content']['itemContent']['tweet_results']['result']['views'].get('count', 0)
    favorite_count = result_entry['favorite_count']
    quote_count = result_entry['quote_count']
    reply_count = result_entry['reply_count']
    retweet_count = result_entry['retweet_count']

    created_date = result_entry['created_at']
    # Wed Dec 18 10:26:13 +0000 2024
    created_date = datetime.strptime(
        created_date, '%a %b %d %H:%M:%S %z %Y').timestamp()
    lang = result_entry['lang']
    quote_id = result_entry.get('quoted_status_id_str', None)
    retweet_id = result_entry.get('retweeted_status_result', {}).get(
        'result', {}).get('rest_id', None)

    entities = result_entry['entities']
    hash_tags = entities.get('hashtags', [])
    hash_tags = [json.dumps(hash_tag, ensure_ascii=False)
                    for hash_tag in hash_tags]
    symbols = entities.get('symbols', [])
    symbols = [json.dumps(symbol, ensure_ascii=False)
                for symbol in symbols]
    cash_tags = entities.get('cash_tags', [])
    cash_tags = [json.dumps(cash_tag, ensure_ascii=False)
                    for cash_tag in cash_tags]
    urls = entities.get('urls', [])
    urls = [json.dumps(url, ensure_ascii=False) for url in urls]
    user_mentions = entities.get('user_mentions', [])
    user_mentions = [json.dumps(
        mention, ensure_ascii=False) for mention in user_mentions]
    images = entities.get('images', [])

    # print(hash_tags, symbols, cash_tags,
    #         urls, user_mentions, images)

    tweet = TweetSchema(query='', tweet_id=tweet_id, user_id=user_id, user_name=user_name, quote_id=quote_id, retweet_id=retweet_id, content=content, view_count=view_count, quote_count=quote_count, favorite_count=favorite_count,
                    reply_count=reply_count, retweet_count=retweet_count, lang=lang, hash_tags=hash_tags, cash_tags=cash_tags, symbols=symbols, urls=urls, user_mentions=user_mentions, images=images, created_date=created_date)
    return tweet


def get_profile_conversation(entry, reply_id=None):
    tweets = []
    items = entry['content']['items']
    for item in items:
        tweet_id = item['entryId'].split('-')[-1]
        item = item['item']['itemContent']
        result_entry = item['tweet_results']['result']['legacy']
        user_id = result_entry['user_id_str']
        user_name = item['tweet_results']['result']['core']['user_results']['result']['legacy']['screen_name']
        content = result_entry['full_text']

        view_count = item['tweet_results']['result']['views'].get(
            'count', 0)
        favorite_count = result_entry['favorite_count']
        quote_count = result_entry['quote_count']
        reply_count = result_entry['reply_count']
        retweet_count = result_entry['retweet_count']

        created_date = result_entry['created_at']
        # Wed Dec 18 10:26:13 +0000 2024
        created_date = datetime.strptime(
            created_date, '%a %b %d %H:%M:%S %z %Y').timestamp()
        lang = result_entry['lang']
        quote_id = result_entry.get('quoted_status_id_str', None)
        retweet_id = result_entry.get('retweeted_status_result', {}).get(
            'result', {}).get('rest_id', None)

        entities = result_entry['entities']
        hash_tags = entities.get('hashtags', [])
        hash_tags = [json.dumps(hash_tag, ensure_ascii=False)
                    for hash_tag in hash_tags]
        symbols = entities.get('symbols', [])
        symbols = [json.dumps(symbol, ensure_ascii=False)
                for symbol in symbols]
        cash_tags = entities.get('cash_tags', [])
        cash_tags = [json.dumps(cash_tag, ensure_ascii=False)
                    for cash_tag in cash_tags]
        urls = entities.get('urls', [])
        urls = [json.dumps(url, ensure_ascii=False) for url in urls]
        user_mentions = entities.get('user_mentions', [])
        user_mentions = [json.dumps(
            mention, ensure_ascii=False) for mention in user_mentions]
        images = entities.get('images', [])

        # print(hash_tags, symbols, cash_tags,
        #     urls, user_mentions, images)

        tweet = TweetSchema(tweet_id=tweet_id, user_id=user_id, user_name=user_name, quote_id=quote_id, retweet_id=retweet_id, reply_id=reply_id, content=content, view_count=view_count, quote_count=quote_count, favorite_count=favorite_count,
                    reply_count=reply_count, retweet_count=retweet_count, lang=lang, hash_tags=hash_tags, cash_tags=cash_tags, symbols=symbols, urls=urls, user_mentions=user_mentions, images=images, created_date=created_date)
        tweets.append(tweet)
    return tweets


def get_tweets(
    user_id: Annotated[str, Field(default='', description="Twitter user ID")],
    count: Annotated[int, Field(default=20, description="Number of tweets to retrieve")],
    cursor: Annotated[str, Field(default='', description="Pagination cursor for fetching next page of tweets")]
) -> list:
    tweets = []
    next_cursor = None
    for _ in range(10):
        try:
            variables = {"userId": str(user_id),
                        "count": count,
                        "includePromotedContent": False,
                        "withQuickPromoteEligibilityTweetFields": False,
                        "withVoice": False,
                        "withV2Timeline": True
                        }

            if cursor and cursor.strip():
                variables['cursor'] = cursor

            next_cursor = None

            variables = quote(json.dumps(variables))
            url = f'https://x.com/i/api/graphql/TK4W-Bktk8AJk0L1QZnkrg/UserTweets?variables={variables}&features=%7B%22profile_label_improvements_pcf_label_in_post_enabled%22%3Afalse%2C%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22premium_content_api_read_enabled%22%3Afalse%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22responsive_web_grok_analyze_button_fetch_trends_enabled%22%3Atrue%2C%22articles_preview_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22creator_subscriptions_quote_tweet_preview_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D&fieldToggles=%7B%22withArticlePlainText%22%3Afalse%7D'
            result = twitter_getter.get_json(url)
            if result:
                try:
                    entries = []
                    for instruction in result['data']['user']['result']['timeline_v2']['timeline']['instructions']:
                        if instruction['type'] == 'TimelineAddEntries':
                            entries = instruction['entries']
                            break

                    for entry in entries:
                        if entry['entryId'].startswith('cursor-bottom'):
                            next_cursor = entry['content']['value']
                        if entry['entryId'].startswith('tweet'):
                            tweet = get_tweet(entry)
                            tweets.append(tweet)    
                        elif entry['entryId'].startswith('profile-conversation'):
                            items = get_profile_conversation(entry)
                            for item in items:
                                tweets.append(item)
                    return tweets, next_cursor
                except Exception:
                    import traceback
                    traceback.print_exc()
                    return [], next_cursor
            return [], next_cursor
        except Exception:
            print(f'trying in ... get tweets {user_id}')
            twitter_getter.rotate_opener()
            logging.error("Rotating opener")
            time.sleep(1)
            continue

    try:
        result = get_user_tweets(user_id=user_id, max_results=count)
        for item in result['data']:
            created_date = datetime.strptime(
                                item['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
            tweet = TweetSchema(
                tweet_id=item['id'],
                content=item['text'],
                created_date=created_date,
                user_id=item['author_id'],
                user_name='',
                lang='',
                view_count=0,
                favorite_count=0,
                quote_count=0,
                reply_count=0,
                retweet_count=0
            )
            tweets.append(tweet)
    except Exception:
        import traceback
        traceback.print_exc()
    return tweets, next_cursor

@timeout_decorator.timeout(10)
def search(
    raw_query: Annotated[str, Field(description="The raw query string to search")],
    count: Annotated[int, Field(default=20, description="Number of results to retrieve")],
    product: Annotated[str, Field(default='Top', description="Type of product to search for (e.g., Top, Latest)")],
    query_source: Annotated[str, Field(default='', description="Source of the query (optional)")],
    cursor: Annotated[str, Field(default=None, description="Pagination cursor for fetching next results")]
) -> List['TweetSchema']:
    """
    Search tweets by raw query
    """
    tweets = []
    next_cursor = None
    try:
        for _ in range(10):
            try:
                variables = {"rawQuery": raw_query,
                            "count": count,
                            "querySource": query_source,
                            "product": product}

                next_cursor = None
                if cursor is not None:
                    variables['cursor'] = cursor

                variables = quote(json.dumps(variables))
                url = f'https://x.com/i/api/graphql/uGjEfWQSYF3MLxu5TVEiRA/SearchTimeline?variables={variables}&features=%7B%22profile_label_improvements_pcf_label_in_post_enabled%22%3Afalse%2C%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22premium_content_api_read_enabled%22%3Afalse%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22responsive_web_grok_analyze_button_fetch_trends_enabled%22%3Atrue%2C%22responsive_web_grok_analyze_post_followups_enabled%22%3Afalse%2C%22articles_preview_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22creator_subscriptions_quote_tweet_preview_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D'
                result = twitter_getter.get_json(url)
                if result:
                    try:
                        entries = []
                        for instruction in result['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']:
                            if instruction['type'] == 'TimelineAddEntries':
                                entries = instruction['entries']
                                break

                        for entry in entries:
                            if entry['entryId'].startswith('cursor-bottom'):
                                next_cursor = entry['content']['value']
                            if not entry['entryId'].startswith('tweet'):
                                continue
                            tweet_id = entry['entryId'].split('-')[-1]
                            result_entry = entry['content']['itemContent']['tweet_results']['result'].get('legacy',  {})
                            if not result_entry:
                                continue
                            content = result_entry['full_text']

                            user_id = entry['content']['itemContent']['tweet_results']['result']['rest_id']
                            user_name = entry['content']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']['screen_name']
                            view_count = entry['content']['itemContent']['tweet_results']['result']['views'].get(
                                'count', 0)
                            favorite_count = result_entry['favorite_count']
                            quote_count = result_entry['quote_count']
                            reply_count = result_entry['reply_count']
                            retweet_count = result_entry['retweet_count']

                            created_date = result_entry['created_at']
                            # Wed Dec 18 10:26:13 +0000 2024
                            created_date = datetime.strptime(
                                created_date, '%a %b %d %H:%M:%S %z %Y').timestamp()
                            lang = result_entry['lang']
                            reply_id = result_entry.get('in_reply_to_status_id_str', None)
                            quote_id = result_entry.get('quoted_status_id_str', None)
                            retweet_id = result_entry.get('retweeted_status_result', {}).get(
                                'result', {}).get('rest_id', None)

                            entities = result_entry['entities']
                            hash_tags = entities.get('hashtags', [])
                            hash_tags = [json.dumps(hash_tag, ensure_ascii=False)
                                        for hash_tag in hash_tags]
                            symbols = entities.get('symbols', [])
                            symbols = [json.dumps(symbol, ensure_ascii=False)
                                    for symbol in symbols]
                            cash_tags = entities.get('cash_tags', [])
                            cash_tags = [json.dumps(cash_tag, ensure_ascii=False)
                                        for cash_tag in cash_tags]
                            urls = entities.get('urls', [])
                            urls = [json.dumps(url, ensure_ascii=False) for url in urls]
                            user_mentions = entities.get('user_mentions', [])
                            user_mentions = [json.dumps(
                                mention, ensure_ascii=False) for mention in user_mentions]
                            images = entities.get('images', [])

                            # print(hash_tags, symbols, cash_tags,
                                # urls, user_mentions, images)

                            tweet = TweetSchema(tweet_id=tweet_id, user_id=user_id, user_name=user_name, quote_id=quote_id, retweet_id=retweet_id, reply_id=reply_id, content=content, view_count=view_count, quote_count=quote_count, favorite_count=favorite_count,
                                        reply_count=reply_count, retweet_count=retweet_count, lang=lang, hash_tags=hash_tags, cash_tags=cash_tags, symbols=symbols, urls=urls, user_mentions=user_mentions, images=images, created_date=created_date)
                            tweets.append(tweet)
                        return tweets, next_cursor
                    except Exception:
                        import traceback
                        traceback.print_exc()
                        return [], next_cursor
                return [], next_cursor
            except Exception:
                import traceback
                traceback.print_exc()
                print(f'trying in ... search {raw_query}')
                twitter_getter.rotate_opener()
                time.sleep(1)
                continue

        try:
            result = search_tweets(query=raw_query, max_results=count)
            for item in result['data']:
                created_date = datetime.strptime(
                                    item['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
                tweet = TweetSchema(
                    tweet_id=item['id'],
                    content=item['text'],
                    created_date=created_date,
                    user_id=item['author_id'],
                    user_name='',
                    lang='',
                    view_count=0,
                    favorite_count=0,
                    quote_count=0,
                    reply_count=0,
                    retweet_count=0
                )
                tweets.append(tweet)
        except Exception:
            import traceback
            traceback.print_exc()
        return tweets, next_cursor
    except timeout_decorator.timeout_decorator.TimeoutError:
        print("Over 10s")
        return None, None
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, None

def get_profile(user_name):
    for _ in range(10):
        try:
            variables = {"screen_name": user_name}
            variables = quote(json.dumps(variables))
            url = f'https://x.com/i/api/graphql/QGIw94L0abhuohrr76cSbw/UserByScreenName?variables={variables}&features=%7B%22hidden_profile_subscriptions_enabled%22%3Atrue%2C%22profile_label_improvements_pcf_label_in_post_enabled%22%3Afalse%2C%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22subscriptions_verification_info_is_identity_verified_enabled%22%3Atrue%2C%22subscriptions_verification_info_verified_since_enabled%22%3Atrue%2C%22highlights_tweets_tab_ui_enabled%22%3Atrue%2C%22responsive_web_twitter_article_notes_tab_enabled%22%3Atrue%2C%22subscriptions_feature_can_gift_premium%22%3Atrue%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%7D&fieldToggles=%7B%22withAuxiliaryUserLabels%22%3Afalse%7D'

            result = twitter_getter.get_json(url)
            if result:
                try:
                    info = result['data']['user']['result']
                    # print(info)
                    user_id = info['rest_id']
                    name = info['legacy']['name']
                    bio = info['legacy']['description']
                    joined_date = datetime.strptime(
                        info['legacy']['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp()
                    follower_count = info['legacy']['followers_count']
                    following_count = info['legacy']['friends_count']
                    favourite_count = info['legacy']['favourites_count']
                    status_count = info['legacy']['statuses_count']
                    verified = info['is_blue_verified']
                    user = UserSchema(user_name=user_name, user_id=user_id, name=name, bio=bio, joined_date=joined_date, follower_count=follower_count,
                                following_count=following_count, favourite_count=favourite_count, status_count=status_count, verified=verified, verified_follower_count=-1)
                    return user
                except Exception:
                    import traceback
                    traceback.print_exc()
                    print(result)
                    return None
            return None
        except Exception:
            print(f'trying in ... get profile {user_name}')
            twitter_getter.rotate_opener()
            
            time.sleep(1)
            continue


def get_user_name_by_user_id(user_id):
    for _ in range(10):
        try:
            url = 'https://api.x.com/1.1/users/show.json'
            result = twitter_getter.get_json(url)
            if result:
                return result
            break
        except Exception:
            import traceback
            traceback.print_exc()
            time.sleep(0.3)
    return None


def get_reply_tweets(parent_tweet_id='', count=20, cursor=''):
    for _ in range(10):
        try:
            print(parent_tweet_id)
            variables = {"focalTweetId": parent_tweet_id,
                        "referrer": "profile",
                        #  "controller_data": "DAACDAABDAABCgABAAAAAAAAAAAKAAkZY3KC3ZuQAAAAAAA=",
                        "with_rux_injections": False,
                        "rankingMode": "Relevance",
                        "includePromotedContent": False,
                        "withCommunity": True,
                        "withQuickPromoteEligibilityTweetFields": True,
                        "withBirdwatchNotes": True,
                        "withVoice": False}
            if cursor and cursor.strip():
                variables['cursor'] = cursor

            next_cursor = None

            variables = quote(json.dumps(variables))
            url = f'https://x.com/i/api/graphql/_u6i0AaqlHR0N7GHWX4y_Q/TweetDetail?variables={variables}&features=%7B%22profile_label_improvements_pcf_label_in_post_enabled%22%3Afalse%2C%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22premium_content_api_read_enabled%22%3Afalse%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22responsive_web_grok_analyze_button_fetch_trends_enabled%22%3Atrue%2C%22responsive_web_grok_analyze_post_followups_enabled%22%3Afalse%2C%22articles_preview_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22creator_subscriptions_quote_tweet_preview_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D&fieldToggles=%7B%22withArticleRichContentState%22%3Atrue%2C%22withArticlePlainText%22%3Afalse%2C%22withGrokAnalyze%22%3Afalse%2C%22withDisallowedReplyControls%22%3Afalse%7D'
            result = twitter_getter.get_json(url)
            if result:
                try:
                    entries = []
                    for instruction in result['data']['threaded_conversation_with_injections_v2']['instructions']:
                        if instruction['type'] == 'TimelineAddEntries':
                            entries = instruction['entries']
                            break
                    tweets = []
                    for entry in entries:
                        if entry['entryId'].startswith('cursor-bottom'):
                            next_cursor = entry['content']['value']
                        if not entry['entryId'].startswith('conversationthread'):
                            continue
                        items = get_profile_conversation(entry, reply_id=parent_tweet_id)
                        for item in items:
                            tweets.append(item)
                    return tweets, next_cursor
                except Exception:
                    import traceback
                    traceback.print_exc()
                    print(result)
                    return [], next_cursor
            return [], next_cursor
        except Exception:
            print('retrying in ...')
            twitter_getter.rotate_opener()
            
            import traceback
            traceback.print_exc()
            time.sleep(1)
            continue
    return [], next_cursor


def get_followings(user_id='', count=20, cursor=''):
    for _ in range(10):
        try:
            # variables = f'%7B%22userId%22%3A%22814419220649877506%22%2C%22count%22%3A20%2C%22includePromotedContent%22%3Atrue%2C%22withQuickPromoteEligibilityTweetFields%22%3Atrue%2C%22withVoice%22%3Atrue%2C%22withV2Timeline%22%3Atrue%7D'
            # decoded = unquote(variables)
            # variables = {"userId":"814419220649877506","count":20,"includePromotedContent":True,"withQuickPromoteEligibilityTweetFields":True,"withVoice":True,"withV2Timeline":True}
            variables = {"userId": str(user_id),
                        "count": count,
                        "includePromotedContent": False}
            next_cursor = None
            if cursor and cursor.strip():
                variables['cursor'] = cursor
            variables = quote(json.dumps(variables))
            url = f'https://x.com/i/api/graphql/gsxNGYhRKA6iYYSInE9qew/Following?variables={variables}&features=%7B%22profile_label_improvements_pcf_label_in_post_enabled%22%3Afalse%2C%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22premium_content_api_read_enabled%22%3Afalse%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22responsive_web_grok_analyze_button_fetch_trends_enabled%22%3Atrue%2C%22articles_preview_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22creator_subscriptions_quote_tweet_preview_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D'
            result = twitter_getter.get_json(url)
            if result:
                try:
                    followings = []
                    entries = []
                    for instruction in result['data']['user']['result']['timeline']['timeline']['instructions']:
                        if instruction['type'] == 'TimelineAddEntries':
                            entries = instruction['entries']
                            break
                    for entry in entries:
                        try:
                            if entry['entryId'].startswith('cursor-bottom'):
                                next_cursor = entry['content']['value']
                            if not entry['entryId'].startswith('user'):
                                continue
                            info = entry['content']['itemContent']['user_results']['result']
                            user_name = info['legacy']['screen_name']
                            user_id = info['rest_id']
                            name = info['legacy']['name']
                            bio = info['legacy']['description']
                            joined_date = datetime.strptime(
                                info['legacy']['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp()
                            follower_count = info['legacy']['followers_count']
                            following_count = info['legacy']['friends_count']
                            favourite_count = info['legacy']['favourites_count']
                            status_count = info['legacy']['statuses_count']
                            verified = info['is_blue_verified']
                            user = UserSchema(user_name=user_name, user_id=user_id, name=name, bio=bio, joined_date=joined_date, follower_count=follower_count,
                                        following_count=following_count, favourite_count=favourite_count, status_count=status_count, verified=verified, verified_follower_count=-1)
                            followings.append(user)
                        except Exception:
                            import traceback
                            traceback.print_exc()        
                            print(entry)
                            print('-' * 10)
                    return followings, next_cursor
                except Exception:
                    import traceback
                    traceback.print_exc()
                    return [], next_cursor
            return [], next_cursor
        except Exception:
            print('trying in ....')
            twitter_getter.rotate_opener()
            
            import traceback
            traceback.print_exc()
            time.sleep(1)
            continue
    return [], next_cursor


def get_followers(user_id='', count=20, cursor=''):
    for _ in range(10):
        try:
            # variables = f'%7B%22userId%22%3A%22814419220649877506%22%2C%22count%22%3A20%2C%22includePromotedContent%22%3Atrue%2C%22withQuickPromoteEligibilityTweetFields%22%3Atrue%2C%22withVoice%22%3Atrue%2C%22withV2Timeline%22%3Atrue%7D'
            # decoded = unquote(variables)
            # variables = {"userId":"814419220649877506","count":20,"includePromotedContent":True,"withQuickPromoteEligibilityTweetFields":True,"withVoice":True,"withV2Timeline":True}
            variables = {"userId": str(user_id),
                        "count": count,
                        "includePromotedContent": False}
            if cursor and cursor.strip():
                variables['cursor'] = cursor
            next_cursor = None
            variables = quote(json.dumps(variables))
            url = f'https://x.com/i/api/graphql/jKKtQ-FpGrW9050ggqY-ag/Followers?variables={variables}&features=%7B%22profile_label_improvements_pcf_label_in_post_enabled%22%3Afalse%2C%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22premium_content_api_read_enabled%22%3Afalse%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22responsive_web_grok_analyze_button_fetch_trends_enabled%22%3Atrue%2C%22responsive_web_grok_analyze_post_followups_enabled%22%3Afalse%2C%22articles_preview_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22creator_subscriptions_quote_tweet_preview_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D'
            result = twitter_getter.get_json(url)
            if result:
                try:
                    followings = []
                    entries = []
                    for instruction in result['data']['user']['result']['timeline']['timeline']['instructions']:
                        if instruction['type'] == 'TimelineAddEntries':
                            entries = instruction['entries']
                            break
                    for entry in entries:
                        if entry['entryId'].startswith('cursor-bottom'):
                                next_cursor = entry['content']['value']
                        if not entry['entryId'].startswith('user'):
                            continue
                        info = entry['content']['itemContent']['user_results']['result']
                        user_name = info['legacy']['screen_name']
                        user_id = info['rest_id']
                        name = info['legacy']['name']
                        bio = info['legacy']['description']
                        joined_date = datetime.strptime(
                            info['legacy']['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp()
                        follower_count = info['legacy']['followers_count']
                        following_count = info['legacy']['friends_count']
                        favourite_count = info['legacy']['favourites_count']
                        status_count = info['legacy']['statuses_count']
                        verified = info['is_blue_verified']
                        user = UserSchema(user_name=user_name, user_id=user_id, name=name, bio=bio, joined_date=joined_date, follower_count=follower_count,
                                    following_count=following_count, favourite_count=favourite_count, status_count=status_count, verified=verified, verified_follower_count=-1)
                        followings.append(user)
                    return followings, next_cursor
                except Exception:
                    import traceback
                    traceback.print_exc()
                    return [], next_cursor
            return [], next_cursor
        except Exception:
            print('trying in ....')
            import traceback
            traceback.print_exc()
            twitter_getter.rotate_opener()
            
            time.sleep(1)
            continue
    return [], next_cursor


def get_user_tweets(user_id: int, max_results: int = 10):
    # Get bearer token from environment
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN") 
    
    # Create URL with user ID
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    
    # Set parameters for tweet fields
    params = {"tweet.fields": "created_at",
              'max_results': max_results,}
    
    # Make request with bearer token auth
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "v2UserTweetsPython"
    }
    
    response = requests.request("GET", url, headers=headers, params=params)
    
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
        
    json_response = response.json()
    return json_response



def search_tweets(
    query: Annotated[str, Field(description="The query string to search for tweets")],
    tweet_fields: Annotated[str, Field(default='text,created_at,author_id', description="Comma-separated list of tweet fields to include in the response")],
    max_results: Annotated[int, Field(default=10, description="Maximum number of tweets to retrieve")],
):
    """
    Search tweets using Twitter API v2
    
    Args:
        query (str): Search query string
        tweet_fields (str): Comma-separated list of tweet fields to return
        
    Returns:
        dict: JSON response from Twitter API
    """
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN") 
    search_url = "https://api.twitter.com/2/tweets/search/all"
    
    # Set up query parameters
    params = {
        'query': query,
        'max_results': max_results,
        'tweet.fields': tweet_fields
    }
    
    # Make authenticated request
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "v2FullArchiveSearchPython"
    }
    
    response = requests.request("GET", search_url, headers=headers, params=params, timeout=10)
    
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
        
    return response.json()


# if __name__ == "__main__":

#     # data = search_tweets(query='6NspJqVFceCiU5D1YgVq7waYoC394Vhqxwg7cSJdFtVE', max_results=10)
#     # data = search_tweets(query='KENJSUYLASHUMfHyy5o4Hp2FdNqZg1AsUPhfH2kYvEP', max_results=10)
#     start_time = datetime.now()
#     for i in range(20):
#         print(f"Time {i+1}")
#         data = search(raw_query='KENJSUYLASHUMfHyy5o4Hp2FdNqZg1AsUPhfH2kYvEP')
#         timing = datetime.now() - start_time

#         print("-"*20)
#         print(timing)
#         print(data)