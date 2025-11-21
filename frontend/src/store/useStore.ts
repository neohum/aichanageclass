import { create } from 'zustand';
import type { School, Student, Rule, Assignment } from '../types';

interface AppState {
  // 현재 학교
  currentSchool: School | null;
  setCurrentSchool: (school: School | null) => void;

  // 학생 목록
  students: Student[];
  setStudents: (students: Student[]) => void;

  // 규칙 목록
  rules: Rule[];
  setRules: (rules: Rule[]) => void;

  // 반편성 목록
  assignments: Assignment[];
  setAssignments: (assignments: Assignment[]) => void;

  // 로딩 상태
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

export const useStore = create<AppState>((set) => ({
  currentSchool: null,
  setCurrentSchool: (school) => set({ currentSchool: school }),

  students: [],
  setStudents: (students) => set({ students }),

  rules: [],
  setRules: (rules) => set({ rules }),

  assignments: [],
  setAssignments: (assignments) => set({ assignments }),

  loading: false,
  setLoading: (loading) => set({ loading }),
}));

