from array import array
from cmath import pi
from itertools import count
from multiprocessing.connection import answer_challenge
from pickletools import read_long1
from typing import List, Any
from xml.etree.ElementTree import PI


def CD(array, minterms):
    # print("CD_array: ", array) 
    # print("CD_minterms: ", minterms)  #어떤 PI들과 minterms들을 대상으로 적용하는지 확인차 출력  그 이후 진행방식은 Row dominance와 거의 유사함
    show = [ ['_'] * (len(minterms) + 1)  for i in range(len(array)+1)  ]
    show[0][0] = "="
    for i in range(len(minterms)):
        show[0][i+1] = minterms[i];
    for i in range(len(array)):
        show[i+1][0] = array[i];
        
    for i in range(1, len(array)+1):
        for j in range(1, len(minterms)+1):
            if show[0][j] in changing( [ show[i][0] ] ):
                show[i][j] = 'v'    #표를 그리는 과정
   
    # for i in range(len(array)+1):
    #     for j in range(len(minterms)+1):
    #         print(show[i][j], end = '|')
    #     print()
    
    reversed_show = [ [] for i in range(len(show[0])-1) ]
    for i in range(1, len(show[0])):
        for j in range(1, len(show)):
            if show[j][i] == 'v':
                reversed_show[i-1].append(show[j][0])
    dominancing = []
    for i in range(len(reversed_show)):
        for j in range(i+1, len(reversed_show)):
            if set(reversed_show[i]).intersection(set(reversed_show[j])) == set(reversed_show[i]):
                if show[0][j+1] not in dominancing:
                    dominancing.append(show[0][j+1])
            if set(reversed_show[j]).intersection(set(reversed_show[i])) == set(reversed_show[j]): 
                if show[0][i+1] not in dominancing:
                    dominancing.append(show[0][i+1])
    #print("dominancing: ",dominancing)
    for i in dominancing:
        minterms.remove(i)
        
    if len(minterms) == 0:
        return 0
    print("minterms: ",minterms)
    RD(array, minterms)
    return 0

def RD(array, minterms):   #PI 리스트와 minterms를 인자로 받음
    # print("RD_array",array)
    # print("RD_minterms",minterms) # 어떤걸로 Row dominance를 하는지 확인차 출력
    EPI(minterms,array)
    
    rd_list = [ [] for i in range(len(array)) ]
    for i in range(len(array)):              #이 반복문을 통해서 각각의 PI들이 cover하는 minterms들을 구해서 rd_list라는 2차원 리스트에 저장한다. 
        for j in changing([array[i]]):
            if j not in minterms:
                continue
            rd_list[i].append(j)
    #print(rd_list)
    dominated = []   #지배당하는 PI들을 담기위한 리스트
    pick_one = []    #서로가 서로를 지배하는 PI들을 담는 리스트
    print_pick_one = []
    for i in range(len(rd_list)):
        for j in range(i+1 , len(rd_list)):
            
            if len(rd_list[i]) == 0 or len(rd_list[j]) == 0:
                pass
            if set(rd_list[i]).intersection(set(rd_list[j])) == set(rd_list[i]) :  #교집합이 rd_list[i]이면, rd_list[j]가 rd_list[i]를 지배한다.
                #print(array[j], " dominates ", array[i] )
                dominated.append(array[i])
            if  set(rd_list[i]).intersection(set(rd_list[j])) == set(rd_list[j]):   #교집합이 rd_list[j]이면, rd_list[i]가 rd_list[j]를 지배한다.
                #print(array[i], " dominates ", array[j] )
                dominated.append(array[j])    
            if rd_list[i] == rd_list[j]:         #서로가 서로를 지배하는 상황이면 후보군중 1개를 택하기 위함
                if array[i] not in pick_one:
                    pick_one.append(array[i])
                    print_pick_one.append([array[i],array[j]])
                if array[j] not in pick_one:
                    pick_one.append(array[j]) 
                    if [array[i],array[j]] not in print_pick_one:
                        print_pick_one.append([array[i],array[j]])
    tmp = []
    for i in print_pick_one:
        for j in i:
            tmp.append(j);
    tmp = list(set(tmp))
    if sorting(tmp) != sorting(sum(print_pick_one,[])):
        print_pick_one = tmp
        
        
    filtered = sorting(list(set(array) - set(dominated)))  #기존에 인자로 들어온 PI중 지배당하는 PI들을 제외해서 filtered라는 리스트에 대입
    result = EPI(minterms, filtered)  #이를 통해 EPI를 구해서 result라는 리스트에 대입한다
    
    used=[]
    for i in minterms:
        for j in result:
            if i in changing([j]):
                used.append(i)     #result에는 EPI가 담겨있을것, -> 더 적용될 수 있으니, EPI가 cover하는 것들을 used라는 리스트에 담아줌              
    left_minterms = sorting(list(set(minterms) - set(used)))  
    
    if(len(result) == 0):  #result의 길이가 0이면 EPI가 없다는 의미
        if len(array) == 0 or len(minterms) == 0:  #남은 PI도 없고 minterms도 없으면, QM Method 종료
            print("Done QM")
        elif len(pick_one) !=0:  #서로가 서로를 지배하는 경우 그 경우의 수를 보여주며, 이중에서 하나를 고르라고 말해줌
            print("Interchangeable: ",print_pick_one)
            new_array = list(set(array) - set((pick_one)))
            result.append(print_pick_one)
            
            for i in changing(pick_one):
                if  i in minterms:
                    minterms.remove(i);
            minterms = sorting(minterms)
            l= EPI(minterms,new_array)
            if(len(l) == 0):
                print(result)
            else:
                CD(new_array, minterms)
        else:
            print("No secondary EPI, Going to CD")  #Row dominance를 적용할 수 없음, Column dominance를 적용
            CD(array, minterms)
    else:               #result의 길이가 0이 아니다 -> EPI가 존재한다는 의미
        print("secondary EPIs by RD:",result)  #EPI값들을 출력해줌
        if len(left_minterms) == 0: #만약 남은 minterms들이 없다면, QM method종료
            print("Done QM")
        else: 
            CD(array, minterms)  #minterms들이 남아있다면, Column dominance의 가능여부 확인 (Column dominance는 9번째 줄로)
    return 0


def EPI(sliced , PIs):
    rel = []
    array = [ ['_'] * (len(sliced) + 1)  for i in range(len(PIs)+2)  ]
    array[0][0] = "="
    array[len(PIs)+1][0] = 'cnt'
    for i in range(len(sliced)):
        array[0][i+1] = sliced[i]
    for i in range(len(PIs)):
        array[i+1][0] = PIs[i]
    
        
    for i in range(1 , len(PIs) + 2):
        for j in range(1 , len(sliced) + 1):
            if array[0][j] in changing([ array[i][0] ]):
                array[i][j] = 'v'
    
    for j in range(1 , len(sliced) + 1):
        cnt = 0
        for i in range(1 , len(PIs) + 2):
            if array[i][j] == 'v':
                cnt+=1
        array[len(PIs)+1][j] = cnt
        
    for j in range(1 , len(sliced) + 1):
        for i in range(1 , len(PIs) + 2):
            if(array[len(PIs)+1][j] == 1):
                if array[i][j] == 'v' and array[i][0] not in rel:
                    rel.append(array[i][0])
                    
    for i in range(len(PIs) + 2): #출력부분 
        for j in range(len(sliced) + 1):
            print(array[i][j],end = '|')
        print()
    return rel


def changing(to_be_changed):
    n = []
    for i in to_be_changed:
        if(i.find('-') == -1):
            n.append(i)
        else:
            key = i.find('-')
            n.append(i[:key] + '0' + i[key+1:])
            n.append(i[:key] + '1' + i[key+1:])
    for j in n:
        if(j.find('-') != -1):
            return changing(n)
    return n



def sorting(unsorted):
    for i in range(len(unsorted)):
        unsorted[i] = unsorted[i].replace('-' , '2')
    unsorted.sort()
    for i in range(len(unsorted)):
        unsorted[i] = unsorted[i].replace('2' , '-')
    return unsorted


def combined(a, b):
    count = 0
    rel = ''
    length = len(a)
    for i in range(length):
        if (a[i] == b[i]):
            rel += a[i]
        else:
            rel += '-'
            count += 1
    if (count != 1):
        return None
    else:
        return rel

                     
    
def solution(minterm):
    answer = []
    im = []
    bi = []
    input_num = minterm[0]
    for i in minterm:
        bi.append( bin(i)[2:].zfill(input_num) )
    sliced = bi[2:]
    sliced = sorted(sliced)
    #print(sliced)
    sliced_2 = sliced.copy()
    while(True):
        com = ['0'] * len(sliced)
        can_do_more = []
        for i in range(len(sliced)-1):
            for j in range(i + 1, len(sliced)):
                rel = combined(sliced[i], sliced[j])
                if (rel != None):
                    if rel not in can_do_more:
                        can_do_more.append(rel)
                    com[i] = 'v'
                    com[j] = 'v'
        for i in range(len(com)):
            if com[i] != 'v':
                if sliced[i] not in im:
                    im.append(sliced[i])
        sliced = can_do_more
        if len(can_do_more) ==0:
            break
    sorted_im = sorting(im)
    a= EPI(sliced_2 , sorted_im)
    b= sorting(a)
    
    answer = sorted_im
    answer.append('EPI')
    for i in b:
        answer.append(i)
    
    for i in range(len(answer)):   #[ (PI들) 'EPI' (EPI들)] 에서 [EPI를 제외한 PI들로 만드는 과정]
        if(answer[i] == "EPI"):
            key = i
            break
    non_epi = answer[:key]
    epi = answer[key+1:]
    non_epi = list(set(non_epi) - set(epi))
    non_epi = sorting(non_epi)
    
    for i in changing(epi):
        for j in sliced_2:
            if i==j:
                sliced_2.remove(j)  # EPI에 사용된 minterms들을 제외하는 과정
    print(answer)
    print()
    RD(non_epi, sliced_2)  #위의 결과로 얻어진 EPI가 아닌 PI들과  EPI가 cover하는 minterms를 제외한 minterms를 Row Dominance시킨다.  (Row Dominance는 53번째 줄로.)
    return "exit"

#cin = [4, 10,0,1,2,5,6,7,8,9,10,14]
#cin = [4, 8,1,3,4,6,9,11,12,14]
#cin = [4,8,1,3,4,5,6,7,9,11]
#cin = [4,8 ,0,1,2,3,7,10,14,15] 
cin = [4,8,0,4,8,10,11,12,13,15]
#cin = [4,9,0,1,2,3,8,9,10,13,15]
#cin = [4,13,0,2,3,6,7,8,9,10,11,12,13,14,15]
#cin = [4, 3, 1,2,3]
#cin = [4,10,0,2,3,4,5,6,11,12,14,15]
#cin = [4,13,0,2,3,4,5,6,7,8,9,10,11,12,13]
#cin = [4,11,0,2,5,6,7,8,10,12,13,14,15]
c = solution(cin)
print(c)