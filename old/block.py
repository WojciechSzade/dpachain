from university import University

class BlockHeader:
    def __init__(self, previous_hash,index,  timestamp, body, signature):
        self.previous_hash = previous_hash
        self.index = index
        self.timestamp = timestamp
        self.root_body_hash = body.calculate_root_hash()
        self.signature = signature
        
class BlockBody:
    def __init__(self, pdf_article, author_article, date_defense_article, university_article, faculty_article):
        self.pdf_article_hash = pdf_article.calculate_hash()
        self.author_article = author_article
        self.date_defense_article = date_defense_article
        self.university_article = university_article
        self.faculty_article = faculty_article
        
    def calculate_root_hash(self):
        pass
    
class Block:
    def __init__(self, previous_hash, index, timestamp, body_data, signature):
        error_message = self.validate_body_data(body_data)
        if error_message:
            raise ValueError(error_message)
        self.body = BlockBody(body_data['pdf_article'], body_data['author_article'], body_data['date_defense_article'], body_data['university_article'], body_data['faculty_article'])
        self.header = BlockHeader(previous_hash, timestamp, self.body, signature)
        
    def validate_body_data(self, body_data):
        if 'pdf_article' not in body_data:
            return False
        if 'author_article' not in body_data:
            return False
        if 'date_defense_article' not in body_data:
            return False
        if 'university_article' not in body_data:
            return False
        if 'faculty_article' not in body_data:
            return False
        if type(body_data['pdf_article']) != str:
            return False
        if type(body_data['author_article']) != str:
            return False
        if type(body_data['date_defense_article']) != str:
            return False
        if type(body_data['university_article']) != University:
            return False
        if type(body_data['faculty_article']) != str:
            return False
        
        return True
        
        