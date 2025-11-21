// 학교
export interface School {
  id: number;
  name: string;
  custom_field_definitions: FieldDefinition[];
  settings: Record<string, any>;
}

// 필드 정의
export interface FieldDefinition {
  name: string;
  type: 'number' | 'text' | 'select' | 'boolean';
  required?: boolean;
  options?: string[];
  min?: number;
  max?: number;
}

// 학생
export interface Student {
  id: number;
  school_id: number;
  grade: number;
  class_number?: number;
  number?: number;
  name: string;
  gender: string;
  custom_fields: Record<string, any>;
}

// 규칙
export interface Rule {
  id: number;
  school_id: number;
  name: string;
  description?: string;
  rule_type: 'balance' | 'constraint' | 'distribution' | 'complex';
  priority: number;
  weight: number;
  rule_definition: RuleDefinition;
  is_active: boolean;
}

export type RuleDefinition = 
  | BalanceRule
  | ConstraintRule
  | DistributionRule
  | ComplexRule;

export interface BalanceRule {
  type: 'balance';
  field: string;
  target: 'equal' | 'average';
  tolerance: number;
}

export interface ConstraintRule {
  type: 'constraint';
  constraint_type: 'separate' | 'together';
  student_ids: number[];
}

export interface DistributionRule {
  type: 'distribution';
  field: string;
  value?: any;
  range?: [number, number];
  strategy: 'spread' | 'limit';
  max_per_class?: number;
}

export interface ComplexRule {
  type: 'complex';
  conditions: Array<{
    field: string;
    operator: string;
    value: any;
  }>;
  action: string;
}

// 반편성
export interface Assignment {
  id: number;
  school_id: number;
  name: string;
  grade: number;
  year: number;
  num_classes: number;
  total_score?: number;
  rule_scores: Record<string, number>;
  statistics: AssignmentStatistics;
  created_at?: string;
}

export interface AssignmentStatistics {
  total_students: number;
  class_sizes: Record<number, number>;
  gender_distribution: Record<number, Record<string, number>>;
  average_scores?: Record<number, number>;
}

export interface AssignmentRequest {
  school_id: number;
  grade: number;
  year: number;
  num_classes: number;
  name: string;
  method?: 'random' | 'greedy' | 'genetic';
  iterations?: number;
}

export interface AssignmentDetail {
  assignment: Assignment;
  classes: Record<number, Student[]>;
}

