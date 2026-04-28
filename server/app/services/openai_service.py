import openai
import logging
import re
from typing import List, Dict, Optional
from ..models.schema import Schema
from ..models.query import Query
import json

logger = logging.getLogger(__name__)


def _strip_markdown_sql_fence(text: str) -> str:
    """Remove common ```sql / ``` wrappers from model output."""
    if not text:
        return text
    text = text.strip()
    fence = re.match(r"^```(?:sql)?\s*\n?(.*)\n?```\s*$", text, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return text


def _completion_message_text(response) -> str:
    """Return assistant message text or raise ValueError if missing."""
    msg = response.choices[0].message if response.choices else None
    raw = getattr(msg, "content", None) if msg else None
    if raw is None or not str(raw).strip():
        raise ValueError("Language model returned no text")
    return str(raw).strip()

class OpenAIService:
    """Service for OpenAI API integration"""
    
    def __init__(self, api_key: str):
        # Initialize OpenAI client without any proxy configuration
        self.client = openai.OpenAI(
            api_key=api_key,
            # Remove any proxy configuration that might be causing issues
        )
        self.model = "gpt-3.5-turbo"
    
    def generate_sql_query(self, user_input: str, project_id: str) -> Dict:
        """Generate SQL query from natural language input"""
        try:
            # Get project schemas
            schemas = Schema.find_by_project(project_id)
            
            if not schemas:
                raise ValueError("No schemas found for this project")
            
            # Format schemas for AI context
            schema_context = self._format_schemas_for_ai(schemas)
            
            # Create prompt for SQL generation
            prompt = self._create_sql_generation_prompt(user_input, schema_context)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse response (content can be None for refusals / some model paths)
            raw_text = _completion_message_text(response)
            sql_query = _strip_markdown_sql_fence(raw_text)
            if not sql_query:
                raise ValueError("Language model returned empty SQL text")
            
            # Generate explanation
            explanation = self._generate_explanation(user_input, sql_query, schema_context)
            
            return {
                'sql_query': sql_query,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            raise e
    
    def _format_schemas_for_ai(self, schemas: List[Schema]) -> str:
        """Format schemas for AI processing"""
        formatted_schemas = []
        
        for schema in schemas:
            formatted_schema = schema.get_formatted_schema_for_ai()
            formatted_schemas.append(formatted_schema)
        
        return "\n\n".join(formatted_schemas)
    
    def _create_sql_generation_prompt(self, user_input: str, schema_context: str) -> str:
        """Create prompt for SQL generation"""
        return f"""
Database Schema:
{schema_context}

User Request: {user_input}

Please generate a SQL query that satisfies the user's request. The query should:
1. Be syntactically correct SQL
2. Use the appropriate tables and columns from the schema
3. Include proper JOINs if multiple tables are needed
4. Use appropriate WHERE clauses for filtering
5. Include ORDER BY if sorting is implied
6. Use LIMIT if the request suggests a limited number of results

Return only the SQL query without any additional explanation.
"""
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for SQL generation"""
        return """You are an expert SQL developer. Your task is to convert natural language requests into accurate SQL queries.

Guidelines:
- Always use proper SQL syntax
- Use appropriate table aliases for clarity
- Include proper JOINs when multiple tables are needed
- Use meaningful column names in SELECT statements
- Add appropriate WHERE clauses for filtering
- Use ORDER BY when sorting is requested
- Use LIMIT when a specific number of results is requested
- Use aggregate functions (COUNT, SUM, AVG, etc.) when appropriate
- Use GROUP BY when aggregating data
- Use HAVING for filtering aggregated results

Return only the SQL query, no explanations or additional text."""
    
    def _generate_explanation(self, user_input: str, sql_query: str, schema_context: str) -> str:
        """Generate explanation for the SQL query"""
        try:
            prompt = f"""
User Request: {user_input}

Generated SQL Query:
{sql_query}

Database Schema:
{schema_context}

Please provide a clear, concise explanation of what this SQL query does in plain English. Focus on:
1. What data is being retrieved
2. Which tables are being used
3. Any filtering or sorting applied
4. The overall purpose of the query

Keep the explanation simple and easy to understand for non-technical users.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that explains SQL queries in simple terms."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return _completion_message_text(response)

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Explanation could not be generated."
    
    def explain_query(self, query_id: str, project_id: str) -> str:
        """Generate detailed explanation for an existing query"""
        try:
            # Get the query
            query = Query.find_by_id(query_id, project_id)
            if not query:
                raise ValueError("Query not found")
            
            # Get project schemas
            schemas = Schema.find_by_project(project_id)
            schema_context = self._format_schemas_for_ai(schemas)
            
            # Generate detailed explanation
            prompt = f"""
SQL Query:
{query.generated_sql}

Original User Request: {query.user_input}

Database Schema:
{schema_context}

Please provide a detailed explanation of this SQL query, including:
1. What each part of the query does
2. How the tables are related
3. What the results will show
4. Any potential performance considerations
5. Alternative ways to write this query

Make the explanation comprehensive but easy to understand.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert SQL developer who provides detailed explanations of SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return _completion_message_text(response)

        except Exception as e:
            logger.error(f"Error explaining query: {e}")
            raise e
    
    def suggest_improvements(self, sql_query: str, project_id: str) -> List[str]:
        """Suggest improvements for a SQL query"""
        try:
            # Get project schemas
            schemas = Schema.find_by_project(project_id)
            schema_context = self._format_schemas_for_ai(schemas)
            
            prompt = f"""
SQL Query:
{sql_query}

Database Schema:
{schema_context}

Please analyze this SQL query and suggest improvements. Consider:
1. Performance optimizations
2. Better readability
3. Security considerations
4. Best practices
5. Alternative approaches

Provide specific, actionable suggestions. Return as a JSON array of strings.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert SQL developer who provides optimization suggestions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            suggestions_text = _completion_message_text(response)
            
            # Try to parse as JSON, fallback to simple list
            try:
                suggestions = json.loads(suggestions_text)
                if isinstance(suggestions, list):
                    return suggestions
            except json.JSONDecodeError:
                pass
            
            # Fallback: split by lines and clean up
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting improvements: {e}")
            return ["Unable to generate suggestions at this time."]
