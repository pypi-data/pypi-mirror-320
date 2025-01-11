import logging
class Logger:
    def __init__(self, log_file='calculation.log', log_level=logging.INFO):
        self.logger = logging.getLogger('test logs')
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            handler.setLevel(log_level)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    def log_message(self, input1,  sign , output ,input2 = 1):
        self.logger.info(f'{input1} {sign} {input2}  = {output}')


# logging.basicConfig(
#     filename='calculator_operations.log',
#     level=logging.INFO,
#     format='%(message)s',
# )
#
# def log_operation(operation, result):
#     print("reeya")
#     logging.info(f"{operation}, {result}")

# log_operation("reeya", 8)
