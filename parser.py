#-*- coding: utf-8 -*-
import BeautifulSoup
import urllib
import sys
from connectDB import DB

#HTML PARSER
#기본 아이디어
# 1. HTML의 strng을 리스트로 만든다
# 2. string이 연속적으로 나오면 그 string의 부모가 body
# 3. 연속적 : index의 차가 10이내

#url을 soup으로 만드는 함수
def makeSoup(url):
    page = urllib.urlopen(url)
    soup = BeautifulSoup.BeautifulSoup(page)
    
    return soup



#html 내 css제거
def deleteCSS(soup):
    try:
	[tag.decompose() for tag in soup("script")]
        body = soup.find('body')
    except:
        body = soup.find('body')
    finally:
        return body


#html body부분에서 string만 뽑아서 리스트로 만듦
def getOnlyString(soup):
    try:
        body = deleteCSS(soup)
        stringList = body.findAll(text=True)
    except:
        stringList = None
    finally:
        return stringList


def isContent(checkNum):
    result = None
    if checkNum == 2:
        result = True
    else:
        result = False
    return result


#String List에서 본문에 해당하는 string의 index3개를 저장
def checkContent(preIndex, curIndex, contentIndex, checkNum):
    isContentGap = 10 # index차이가 10이면 같은 div에 속함
    if (curIndex - preIndex) < isContentGap:
        contentIndex[checkNum] = preIndex
        contentIndex[checkNum+1] = curIndex
        checkNum += 1
    else:
        checkNum = 0
    return checkNum


#string list에서 100자가 넘는 string만 index체크
#연속적으로 3번 나오면 그것의 부모는 본문
#연속적은 그 차이가 10
# 결과 : content의 index값을 얻는 것
def getContentIndex(stringList, contentIndex):
    preIndex = 0
    curIndex = 0
    checkNum = 0
    isStringLen = 100 #글자의 길이가 100자는 넘어야 본문
    
    for line in stringList:
        
        if len(line) > isStringLen:
            checkNum = checkContent(preIndex, curIndex, contentIndex, checkNum)
            preIndex = curIndex
            if isContent(checkNum):
                break
        curIndex += 1
    
    if contentIndex[2] == 0:
        contentIndex[2] = contentIndex[1]
    return contentIndex

def insertTagId(tag, id):
    isLastTagId = 5
    try:
        if id == isLastTagId:
            return
        parentTag = tag.parent
        parentTag['id'] = id
        insertTagId(parentTag, id+1)
    except:
        #id값이 없는 경우 if절에서 에러 -> 이 함수를 종료
        return


def findContentId(tag, count):
    parentTag = tag.parent
    tagId = [0, 1, 2, 3, 4]
    if count is 4:
        return
    try:
        if (parentTag['id'] in tagId) and (parentTag.name == "div"):
            return parentTag['id']
        else:
            return findContentId(parentTag, count+1)
    except:
        return findContentId(parentTag, count+1)


def getContentId(stringList, contentIndexList):
    contentID = 0
    
    content2Tag = stringList[contentIndexList[1]]
    content3Tag = stringList[contentIndexList[2]]
    
    content2ID = findContentId(content2Tag, 0)
    content3ID = findContentId(content3Tag, 0)
    
    if content3ID>content2ID:
        contentID = content3ID
    else:
        contentID = content2ID
    
    return contentID


def selectBody(soup, contentID):
    global dbContents
    
    contents = soup.find("div", {"id" : contentID})
    del contents['id']
    
    html = contents.prettify()
    dbContents = html

def parsing(url):
    soup = makeSoup(url)
    global dbTitle
    title = soup.title.string
    dbTitle = str(title)
    stringList = getOnlyString(soup)
    contentIndex = [0, 0, 0]
    if stringList is not None:
        getContentIndex(stringList, contentIndex)
        contentFirstLine = stringList[contentIndex[0]]
        insertTagId(contentFirstLine, 0)
        contentID = getContentId(stringList, contentIndex)
        selectBody(soup, contentID)
    
    else:
        #parsing error
        return

##run
try:
    dbUrl = sys.argv[1]
    parsing(dbUrl)
    db = DB()
    db.insertParserHTML(dbTitle, dbUrl, dbContents)
    print "SUCCESS"
except:
    print "FAIL"
