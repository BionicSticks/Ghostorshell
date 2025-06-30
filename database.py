import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    text_length = Column(Integer, nullable=False)
    ai_probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String(45), nullable=True)  # For basic tracking
    visitor_id = Column(String(64), nullable=True)  # Unique visitor identifier

class VisitorCredit(Base):
    __tablename__ = "visitor_credits"
    
    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(String(64), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    credits_remaining = Column(Integer, default=1, nullable=False)  # Start with 1 free credit
    total_purchased = Column(Integer, default=0, nullable=False)  # Track total credits purchased
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    stripe_payment_id = Column(String(255), nullable=True)  # For payment tracking
    
class DatabaseManager:
    def __init__(self):
        """Initialize database manager and create tables"""
        Base.metadata.create_all(bind=engine)
    
    def get_session(self):
        """Get database session"""
        return SessionLocal()
    
    def save_analysis(self, filename, file_type, file_size, text_length, 
                     ai_probability, confidence, reasoning, ip_address=None, visitor_id=None):
        """
        Save analysis results to database
        
        Args:
            filename: Name of the analyzed file
            file_type: Type/extension of the file
            file_size: Size of file in bytes
            text_length: Length of extracted text
            ai_probability: AI detection probability (0-1)
            confidence: Confidence score (0-1)
            reasoning: Analysis reasoning text
            ip_address: Client IP address (optional)
            visitor_id: Unique visitor identifier (optional)
            
        Returns:
            int: ID of the saved record
        """
        session = self.get_session()
        try:
            record = AnalysisRecord(
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                text_length=text_length,
                ai_probability=ai_probability,
                confidence=confidence,
                reasoning=reasoning,
                ip_address=ip_address,
                visitor_id=visitor_id
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record.id
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to save analysis: {e}")
        finally:
            session.close()
    
    def get_recent_analyses(self, limit=50):
        """
        Get recent analysis records
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            list: List of analysis records
        """
        session = self.get_session()
        try:
            records = session.query(AnalysisRecord)\
                           .order_by(AnalysisRecord.created_at.desc())\
                           .limit(limit)\
                           .all()
            return records
        finally:
            session.close()
    
    def get_analysis_stats(self):
        """
        Get analysis statistics
        
        Returns:
            dict: Statistics about analyses
        """
        session = self.get_session()
        try:
            total_analyses = session.query(AnalysisRecord).count()
            
            # Get AI vs Human detection percentages
            ai_detected = session.query(AnalysisRecord)\
                               .filter(AnalysisRecord.ai_probability >= 0.5)\
                               .count()
            
            human_detected = total_analyses - ai_detected
            
            # Average confidence
            avg_confidence = session.query(AnalysisRecord.confidence).all()
            avg_conf = sum([r[0] for r in avg_confidence]) / len(avg_confidence) if avg_confidence else 0
            
            # File type distribution
            file_types = session.query(AnalysisRecord.file_type).all()
            file_type_counts = {}
            for ft in file_types:
                file_type_counts[ft[0]] = file_type_counts.get(ft[0], 0) + 1
            
            return {
                'total_analyses': total_analyses,
                'ai_detected': ai_detected,
                'human_detected': human_detected,
                'ai_percentage': (ai_detected / total_analyses * 100) if total_analyses > 0 else 0,
                'human_percentage': (human_detected / total_analyses * 100) if total_analyses > 0 else 0,
                'average_confidence': avg_conf,
                'file_type_distribution': file_type_counts
            }
        finally:
            session.close()
    
    def get_analyses_list(self, limit=1000):
        """
        Get analyses as list of dictionaries
        
        Args:
            limit: Maximum number of records
            
        Returns:
            list: Analysis data as dictionaries
        """
        session = self.get_session()
        try:
            records = session.query(AnalysisRecord)\
                           .order_by(AnalysisRecord.created_at.desc())\
                           .limit(limit)\
                           .all()
            
            result = []
            for record in records:
                result.append({
                    'filename': record.filename,
                    'file_type': record.file_type,
                    'file_size': record.file_size,
                    'text_length': record.text_length,
                    'ai_probability': record.ai_probability,
                    'confidence': record.confidence,
                    'created_at': record.created_at,
                    'reasoning': record.reasoning
                })
            return result
        finally:
            session.close()
    
    def delete_old_records(self, days_old=30):
        """
        Delete records older than specified days
        
        Args:
            days_old: Number of days to keep records
            
        Returns:
            int: Number of deleted records
        """
        session = self.get_session()
        try:
            cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_old)
            deleted = session.query(AnalysisRecord)\
                           .filter(AnalysisRecord.created_at < cutoff_date)\
                           .delete()
            session.commit()
            return deleted
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to delete old records: {e}")
        finally:
            session.close()

    def get_visitor_credits(self, visitor_id):
        """
        Get visitor credit information
        
        Args:
            visitor_id: Unique visitor identifier
            
        Returns:
            VisitorCredit object or None
        """
        session = self.get_session()
        try:
            return session.query(VisitorCredit).filter(
                VisitorCredit.visitor_id == visitor_id
            ).first()
        except Exception as e:
            return None
        finally:
            session.close()

    def create_visitor_credit(self, visitor_id, ip_address):
        """
        Create new visitor credit record with 1 free credit
        
        Args:
            visitor_id: Unique visitor identifier
            ip_address: Client IP address
            
        Returns:
            VisitorCredit object
        """
        session = self.get_session()
        try:
            visitor_credit = VisitorCredit(
                visitor_id=visitor_id,
                ip_address=ip_address,
                credits_remaining=1
            )
            
            session.add(visitor_credit)
            session.commit()
            session.refresh(visitor_credit)
            return visitor_credit
            
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to create visitor credit: {e}")
        finally:
            session.close()

    def use_credit(self, visitor_id):
        """
        Deduct one credit from visitor's account
        
        Args:
            visitor_id: Unique visitor identifier
            
        Returns:
            bool: True if credit was successfully deducted
        """
        session = self.get_session()
        try:
            visitor_credit = session.query(VisitorCredit).filter(
                VisitorCredit.visitor_id == visitor_id
            ).first()
            
            if visitor_credit and visitor_credit.credits_remaining > 0:
                visitor_credit.credits_remaining -= 1
                visitor_credit.last_activity = datetime.datetime.utcnow()
                session.commit()
                return True
            
            return False
            
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

    def add_credits(self, visitor_id, credits_to_add, stripe_payment_id=None):
        """
        Add credits to visitor's account (after payment)
        
        Args:
            visitor_id: Unique visitor identifier
            credits_to_add: Number of credits to add
            stripe_payment_id: Stripe payment ID for tracking
            
        Returns:
            bool: True if credits were successfully added
        """
        session = self.get_session()
        try:
            visitor_credit = session.query(VisitorCredit).filter(
                VisitorCredit.visitor_id == visitor_id
            ).first()
            
            if visitor_credit:
                visitor_credit.credits_remaining += credits_to_add
                visitor_credit.total_purchased += credits_to_add
                visitor_credit.last_activity = datetime.datetime.utcnow()
                if stripe_payment_id:
                    visitor_credit.stripe_payment_id = stripe_payment_id
                session.commit()
                return True
            
            return False
            
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()