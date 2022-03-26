from threading import Thread
import time

def Decoratore(funzione):
    def prova(a,b):
        print('ho decorato la gunzione pippo')
        return funzione(a,b)
    return prova

class Decorazione(Thread):

    def __init__(self,func):
        self.funzione = func

    def __call__(self,*args):
        print("la funzione sta partendo")
        return Thread(target=self.funzione,args=[*args]).start()

@Decorazione
def pippo(a):
    for i in range(a):
        time.sleep(1)
        print(i)

if __name__ == '__main__':
    pippo(4)
    print('ciao')