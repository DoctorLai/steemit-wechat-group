# high rep constant
HIGH_REP = 74
# minimal post length to get vote
MIN_POST_LENGTH = 200
# minimal valid posting percentage
MIN_VALUE = 1
# maximum valid posting percentage
MAX_VALUE = 40
# minimal SP to be voted
MIN_SP = 5 
# bonus for witness vote
BONUS_WITNESS = 5
# bonus for member
BONUS_MEMBER = 1
# bonus for voting back
BONUS_VOTING_BACK = 5    
# upperbound value for voting back e.g. 20000 = 2 x 100% votes
MAX_VOTE_BACK = 20000 
# forbidden post tags
BLACKLIST_TAGS = ['test', 'cn-shui', 'nsfw']
# bonus post tags
BONUS_TAGS = { 'cn-activity': 1.0, 'cn': 1, 'cn-curation' : 2.0,  'cn-reader': 3.0, 'hive-180932': 2.0}
# tags we don't like
LESS_TAGS = { 'stats': 0.55, 'cn-stats': 0.55, 'steem-stats': 0.55, 'steemit-stats': 0.55, 'statistics': 0.55, 'actifit': 0.6 }
# weight for user's delegation comparing to global
W_DELEGATION = [ (1500, 1.2), (900, 1), (600, 0.6), (350, 0.2), (150, 0.18), (100, 0.10), (50, 0.07), (0, 0.05) ]
# weight for user's delegation comparing to his/her own SP
W_DELEGATION_USER = 0.25
# weight for user's reputation
W_REP = 0.2
# adjustment according to different levels
ADJUSTMENTS = [ (15, 0.10), (50, 0.15), (100, 0.2), (250, 0.25), (350, 0.3), (600, 0.35), (800, 0.40), (1000, 0.45), (1200, 0.5), (1350, 0.6), (1600, 0.65), (2000, 0.76), (2200, 0.8), (2500, 1) ]
# downvoters in last 7 days => don't vote
DOWNVOTERS = ["buildawhale", "themarkymark", "spaminator", "mack-bot", "steemcleaners", "blockcleaner"]
        
# return a voting value from MIN_VALUE to MAX_VALUE 
def bank_getvp(
    delegated,          # the user delegated SP amount e.g. 100 
    user_sp,            # the user's own SP e.g. 200 
    bot_vp,             # the bot's VP e.g. 50
    total_delegated,    # the total SP delegated to bank e.g. 30000 
    user_rep,           # the users reputation e.g. 70 
    tags,               # tags e.g. ['cn', 'programming'] 
    title,              # post's title string e.g. "Hello" 
    body,               # post's body string e.g. "Hello, world!"  
    is_member,          # is user part of the wechat member? 
    witness_vote,       # has the user voted @justyy as witness?    
    votes_back,         # total sum(weight) from user to justyy or dailychina e.g. 100,00
    downvoters7d = []   # downvoters in last 7 days
    ):            
    # filter out posts that author has been downvoted in the last 7 days, sorry.
    if [x in downvoters7d for x in DOWNVOTERS].count(True) > 0:
        return 0 
    global HIGH_REP, MIN_POST_LENGTH, MIN_VALUE, MAX_VALUE, MIN_SP, BONUS_WITNESS, BONUS_MEMBER, BLACKLIST_TAGS, BONUS_TAGS
    # not voting for delegation less than e.g. 5 SP
    if delegated < MIN_SP:
        return 0        
    # filter out posts containing the blacklist tags
    if [x in tags for x in BLACKLIST_TAGS].count(True) > 0:
        return 0
    # post too short
    if len(body) < MIN_POST_LENGTH:
        return 0           
    # check if containing bonus tags
    bonus = 0
    for _ in tags:
        if _ in BONUS_TAGS:
            bonus += BONUS_TAGS[_]
            # only 1 maximum bonus tag
            break
    # bonus for witness vote            
    if witness_vote:
        bonus += BONUS_WITNESS
    # bonus for being a wechat member
    if is_member:
        bonus += BONUS_MEMBER                   
    def norm(x, total):
        y = min(1, x / total)
        y = max(0, y)        
        return 1 - 1 / (1 + y)
    # bonus for voting back
    if votes_back > 0:
        bonus += BONUS_VOTING_BACK * norm(votes_back, MAX_VOTE_BACK)        
    score = 0                
    # the higher percentage user's delegation comparing to all delegated SP, the better 
    for _ in W_DELEGATION:
        if delegated >= _[0]:
            score += _[1] * norm(delegated, total_delegated)
            break
    # add a linear part
    score += delegated / total_delegated 
    # the higher percentage user's delegation per own SP, the better
    score += W_DELEGATION_USER * norm(delegated, user_rep)
    # the higher reputation, the better
    score += W_REP * norm(user_rep, HIGH_REP)
    # scale to [0, 100]
    score *= 100
    # and we have bonus
    score += bonus    
    # adjustment
    for _ in ADJUSTMENTS:
      if delegated < _[0]:
        score *= _[1]
        break
    # tags we don't like
    for _ in tags:
        if _ in LESS_TAGS:
            score *= LESS_TAGS[_]
            # only 1 maximum less tag
            break    
    # more writing
    score += min(5, (len(body) - MIN_POST_LENGTH) / 1000)                  
    # adjust to bot's VP
    score = score * (bot_vp / 100)
    if bot_vp <= 95:
        score *= 0.9
    elif bot_vp <= 90:
        score *= 0.85
    elif bot_vp <= 85:
        score *= 0.80
    else:
        score *= 0.75        
    # limit to range
    score = max(MIN_VALUE, score)
    score = min(MAX_VALUE, score)
    return score
    
if __name__ == "__main__":
    title = "title"
    def assertScore(expected, score, eps = 0.001):
      if abs(expected - score) <= eps:
        print("Test passed with ", expected)
      else:
        print("Test Failed: expected ", expected, "but got ", score)  
    body = ("X" * MIN_POST_LENGTH)[:MIN_POST_LENGTH]
    
    scores = [0, 3.3616074821011614, 4.357578692149988, 5.412278241102609, 6.125797486502999, 8.04691378635907, 8.293524623480668, 10.177007952494314, 10.357341381168414, 14.541985108121784, 14.908552342842388, 16.429144356955383, 18.098874970174183, 22.89648071875631, 0, 0]
    assertScore(scores[0], bank_getvp(5, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000, ["spaminator", "spaminator", "steemcleaners"]))
    assertScore(scores[1], bank_getvp(10, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[2], bank_getvp(15, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[3], bank_getvp(20, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[4], bank_getvp(30, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[5], bank_getvp(50, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[6], bank_getvp(75, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[7], bank_getvp(100, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[8], bank_getvp(200, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[8], bank_getvp(300, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[8], bank_getvp(349, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[9], bank_getvp(350, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[9], bank_getvp(450, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[10], bank_getvp(550, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[11], bank_getvp(650, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000, ['a', 'a', 'b']))
    assertScore(scores[12], bank_getvp(700, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[12], bank_getvp(800, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[12], bank_getvp(900, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[12], bank_getvp(1000, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(1200, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(1600, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(1700, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(1800, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(1900, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(2000, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(2100, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(2200, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(2300, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(2400, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[13], bank_getvp(2500, 3000, 90, 600000, 55, ["cn"], title, body, True, True, 10000))
    assertScore(scores[14], bank_getvp(1600, 20000, 90, 600000, 55, ["cn"], title, body, True, True, 10000, set(["steemcleaners", "a", "steemcleaner", "spaminator", "spaminator"])))
    assertScore(scores[15], bank_getvp(2500, 20000, 90, 600000, 55, ["cn", 'stats'], title, body, True, True, 10000, {"steemcleaners"}))    
