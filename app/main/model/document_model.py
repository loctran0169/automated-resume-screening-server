from sqlalchemy.orm import backref
from app.main.model.candidate_model import candidate_documents
from .. import db

class DocumentModel(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(510), nullable=False)

    candidate = db.relationship('CandidateModel', secondary= candidate_documents, back_populates="document")
    
    def __repr__(self):
        return "<documents: '{}'>".format(self.name)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url        
        }