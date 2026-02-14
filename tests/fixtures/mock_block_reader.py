def mock_read_block_output(partition, block_size, inode):
    return f"Lorem ipsum - partition = {partition}, block_size = {block_size}, inode = {inode}".encode()
