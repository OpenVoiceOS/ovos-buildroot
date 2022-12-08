"""A simple function to print a list"""
def print_list(the_list,iden=False,level=0):
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_list(each_item,iden,level+1)
                else:
                     if iden:
                         for tab_stop in range(level):
                                print("\t",end='')
                     print(each_item)
