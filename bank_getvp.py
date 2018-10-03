# high rep constant
HIGH_REP = 72
# minimal post length to get vote
MIN_POST_LENGTH = 2
# minimal valid posting percentage
MIN_VALUE = 0.5
# maximum valid posting percentage
MAX_VALUE = 50
# minimal SP to be voted
MIN_SP = 5 
# bonus for witness vote
BONUS_WITNESS = 1
# bonus for member
BONUS_MEMBER = 0.5
# bonus for voting back
BONUS_VOTING_BACK = 5    
# upperbound value for voting back e.g. 20000 = 2 x 100% votes
MAX_VOTE_BACK = 20000 
# forbidden post tags
BLACKLIST_TAGS = ['test', 'cn-shui', 'nsfw']
# bonus post tags
BONUS_TAGS = { 'cn-activity': 2.0 }
# weight for user's delegation comparing to global
W_DELEGATION = { 1000: 1.2, 900: 1, 600: 0.7, 350: 0.45, 150: 0.3, 100: 0.15, 50: 0.1, 0: 0.05 }
# weight for user's delegation comparing to his/her own SP
W_DELEGATION_USER = 0.3
# weight for user's reputation
W_REP = 0.2

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
    votes_back,         # total sum(weight) from user to justyy or dailychina e.g. 100,00
    witness_vote):      # has the user voted @justyy as witness?
    global HIGH_REP, MIN_POST_LENGTH, MIN_VALUE, MAX_VALUE, MIN_SP, BONUS_WITNESS, BONUS_MEMBER, BLACKLIST_TAGS, BONUS_TAGS
    # not voting for delegation less than e.g. 5 SP
    if total_delegated < MIN_SP:
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
        if delegated >= _:
            score += W_DELEGATION[_] * norm(delegated, total_delegated)
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
    # adjust to bot's VP
    score = score * bot_vp / 100
    # adjustment
    if delegated <= 100:
        score *= 0.6
    elif delegated <= 350:
        score *= 0.75
    elif delegated <= 600:
        score *= 0.9
    # limit to range
    score = max(MIN_VALUE, score)
    score = min(MAX_VALUE, score)
    return score
    
if __name__ == "__main__":
    print(bank_getvp(5, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(10, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(15, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(20, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(30, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(50, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(75, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(100, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(200, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(350, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(500, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(600, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(800, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(1200, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(1600, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))
    print(bank_getvp(2500, 20000, 80, 30000, 55, ["cn"], "title", "at least 200 here", True, True, 10000))    
