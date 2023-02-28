import os 


blocks_folder = 'blocks'
blocks = os.listdir(blocks_folder)

for i in range(1, len(blocks)):
    os.remove(blocks_folder + '/' + blocks[i])

db_folder = 'chainstate'
db_files = os.listdir(db_folder)
for i in range(len(db_files)):
    os.remove(db_folder + '/' + db_files[i])

with open('mempool/mempool.dat', 'wb'):
    pass