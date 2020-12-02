from googletrans import Translator

class Class_Translate:
    # https://py-googletrans.readthedocs.io/en/latest/

    def __init__(self):
        print('Class_Translate..__init__')
        return

    def trans(self, trans_src):
        translator = Translator()
        tran = translator.translate(trans_src,src='auto',dest='ko')
        return tran.text  #, tran.pronunciation

def main(args):
    lib_trans = Class_Translate()
    text,pronunciation = lib_trans.trans(args)
    print(text)
    #print(pronunciation)

if __name__ == '__main__':
    main("hello world")
