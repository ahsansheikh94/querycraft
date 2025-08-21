import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Plus, 
  Edit, 
  Trash2, 
  Database,
  Save,
  X,
  Copy,
  Check
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import Header from '../../components/layout/Header';
import { Schema, SchemaInput } from '../../types';
import apiService from '../../lib/api';
import { formatDate, copyToClipboard } from '../../lib/utils';
import toast from 'react-hot-toast';

interface SchemaFormData {
  table_name: string;
  table_schema: string;
}

export default function SchemaPage() {
  const { id: projectId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isCreating, setIsCreating] = useState(false);
  const [editingSchema, setEditingSchema] = useState<Schema | null>(null);
  const [formData, setFormData] = useState<SchemaFormData>({
    table_name: '',
    table_schema: ''
  });

  // Fetch project details
  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiService.getProject(projectId!),
    enabled: !!projectId,
  });

  // Fetch schemas
  const { data: schemasData, isLoading } = useQuery({
    queryKey: ['schemas', projectId],
    queryFn: () => apiService.getSchemas(projectId!),
    enabled: !!projectId,
  });

  // Create/Update schema mutation
  const schemaMutation = useMutation({
    mutationFn: (schemas: SchemaInput[]) => 
      editingSchema 
        ? apiService.updateSchema(projectId!, schemas)
        : apiService.createSchema(projectId!, schemas),
    onSuccess: () => {
      toast.success(editingSchema ? 'Schema updated successfully!' : 'Schema created successfully!');
      queryClient.invalidateQueries({ queryKey: ['schemas', projectId] });
      queryClient.invalidateQueries({ queryKey: ['project-stats', projectId] });
      setIsCreating(false);
      setEditingSchema(null);
      setFormData({ table_name: '', table_schema: '' });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to save schema');
    },
  });

  // Delete schema mutation
  const deleteSchemaMutation = useMutation({
    mutationFn: (schemaId: string) => apiService.deleteSchema(projectId!, schemaId),
    onSuccess: () => {
      toast.success('Schema deleted successfully!');
      queryClient.invalidateQueries({ queryKey: ['schemas', projectId] });
      queryClient.invalidateQueries({ queryKey: ['project-stats', projectId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to delete schema');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const schemaJson = JSON.parse(formData.table_schema);
      const schemaInput: SchemaInput = {
        table_name: formData.table_name,
        table_schema: schemaJson
      };
      
      schemaMutation.mutate([schemaInput]);
    } catch (error) {
      toast.error('Invalid JSON format for schema');
    }
  };

  const handleEdit = (schema: Schema) => {
    setEditingSchema(schema);
    setFormData({
      table_name: schema.table_name,
      table_schema: JSON.stringify(schema.table_schema, null, 2)
    });
  };

  const handleDelete = (schemaId: string) => {
    if (confirm('Are you sure you want to delete this schema?')) {
      deleteSchemaMutation.mutate(schemaId);
    }
  };

  const handleCopySchema = async (schema: Schema) => {
    try {
      await copyToClipboard(JSON.stringify(schema.table_schema, null, 2));
      toast.success('Schema copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy schema');
    }
  };

  const sampleSchema = {
    columns: [
      { name: "id", type: "INTEGER", primary_key: true },
      { name: "name", type: "VARCHAR(100)", not_null: true },
      { name: "email", type: "VARCHAR(255)", unique: true },
      { name: "created_at", type: "TIMESTAMP", not_null: true }
    ]
  };

  return (
    <div className="min-h-screen">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => navigate(`/project/${projectId}`)}
                className="p-2"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold gradient-text">
                  {project?.name} - Schemas
                </h1>
                <p className="text-muted-foreground">
                  Manage your database table schemas
                </p>
              </div>
            </div>
            <Button
              onClick={() => setIsCreating(true)}
              className="gradient"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Schema
            </Button>
          </div>
        </motion.div>

        {/* Create/Edit Schema Form */}
        {(isCreating || editingSchema) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <Card className="glass-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>
                      {editingSchema ? 'Edit Schema' : 'Create New Schema'}
                    </CardTitle>
                    <CardDescription>
                      Define your table structure in JSON format
                    </CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setIsCreating(false);
                      setEditingSchema(null);
                      setFormData({ table_name: '', table_schema: '' });
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="table_name">Table Name *</Label>
                    <Input
                      id="table_name"
                      value={formData.table_name}
                      onChange={(e) => setFormData({ ...formData, table_name: e.target.value })}
                      placeholder="e.g., users, products, orders"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="table_schema">Schema JSON *</Label>
                    <Textarea
                      id="table_schema"
                      value={formData.table_schema}
                      onChange={(e) => setFormData({ ...formData, table_schema: e.target.value })}
                      placeholder={JSON.stringify(sampleSchema, null, 2)}
                      rows={10}
                      className="font-mono text-sm"
                      required
                    />
                    <p className="text-xs text-muted-foreground">
                      Define your table columns in JSON format. Include name, type, and constraints.
                    </p>
                  </div>

                  <div className="flex items-center justify-end space-x-4 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setIsCreating(false);
                        setEditingSchema(null);
                        setFormData({ table_name: '', table_schema: '' });
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      className="gradient"
                      disabled={schemaMutation.isPending}
                    >
                      {schemaMutation.isPending ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Saving...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <Save className="h-4 w-4" />
                          <span>{editingSchema ? 'Update Schema' : 'Create Schema'}</span>
                        </div>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Schemas List */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="glass-card">
                <CardContent className="p-6">
                  <div className="animate-pulse">
                    <div className="h-4 bg-white/10 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-white/10 rounded w-1/2 mb-4"></div>
                    <div className="space-y-2">
                      <div className="h-3 bg-white/10 rounded w-1/4"></div>
                      <div className="h-3 bg-white/10 rounded w-1/3"></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : schemasData?.schemas.length === 0 ? (
          <Card className="glass-card">
            <CardContent className="p-8 text-center">
              <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No schemas yet</h3>
              <p className="text-muted-foreground mb-6">
                Add your first database schema to start generating SQL queries
              </p>
              <Button onClick={() => setIsCreating(true)} className="gradient">
                <Plus className="h-4 w-4 mr-2" />
                Add Schema
              </Button>
            </CardContent>
          </Card>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {schemasData?.schemas.map((schema) => (
              <motion.div
                key={schema.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <Card className="glass-card">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{schema.table_name}</CardTitle>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopySchema(schema)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(schema)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(schema.id)}
                          className="text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="text-sm text-muted-foreground">
                        <span className="font-medium">Columns:</span> {schema.table_schema.columns.length}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Created: {formatDate(schema.created_at)}
                      </div>
                      <div className="pt-2">
                        <details className="text-sm">
                          <summary className="cursor-pointer hover:text-foreground">
                            View Schema Structure
                          </summary>
                          <pre className="mt-2 p-2 bg-white/5 rounded text-xs overflow-x-auto">
                            {JSON.stringify(schema.table_schema, null, 2)}
                          </pre>
                        </details>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}
      </main>
    </div>
  );
}


