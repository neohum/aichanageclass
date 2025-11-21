import { useEffect, useState } from 'react';
import { 
  Button, 
  Table, 
  Upload, 
  message, 
  Space, 
  Modal, 
  Form, 
  Input, 
  Select,
  Popconfirm 
} from 'antd';
import { UploadOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useStore } from '../store/useStore';
import { studentApi } from '../api';
import type { Student } from '../types';

export const Students = () => {
  const { currentSchool, students, setStudents, setLoading } = useStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    if (currentSchool) {
      loadStudents();
    }
  }, [currentSchool]);

  const loadStudents = async () => {
    if (!currentSchool) return;
    
    try {
      setLoading(true);
      const response = await studentApi.getAll(currentSchool.id);
      setStudents(response.data);
    } catch (error) {
      message.error('학생 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file: File) => {
    if (!currentSchool) {
      message.error('학교를 먼저 선택해주세요.');
      return false;
    }

    try {
      setLoading(true);
      await studentApi.uploadExcel(currentSchool.id, file);
      message.success('Excel 파일이 성공적으로 업로드되었습니다.');
      loadStudents();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Excel 업로드에 실패했습니다.');
    } finally {
      setLoading(false);
    }

    return false; // 자동 업로드 방지
  };

  const handleSave = async (values: any) => {
    try {
      setLoading(true);
      if (editingStudent) {
        await studentApi.update(editingStudent.id, values);
        message.success('학생 정보가 수정되었습니다.');
      } else {
        await studentApi.create({ ...values, school_id: currentSchool?.id });
        message.success('학생이 추가되었습니다.');
      }
      setIsModalOpen(false);
      form.resetFields();
      setEditingStudent(null);
      loadStudents();
    } catch (error) {
      message.error('저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setLoading(true);
      await studentApi.delete(id);
      message.success('학생이 삭제되었습니다.');
      loadStudents();
    } catch (error) {
      message.error('삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (student: Student) => {
    setEditingStudent(student);
    form.setFieldsValue(student);
    setIsModalOpen(true);
  };

  const columns: ColumnsType<Student> = [
    { title: '학년', dataIndex: 'grade', key: 'grade', width: 80 },
    { title: '번호', dataIndex: 'number', key: 'number', width: 80 },
    { title: '이름', dataIndex: 'name', key: 'name', width: 120 },
    { title: '성별', dataIndex: 'gender', key: 'gender', width: 80 },
    {
      title: '작업',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record)}
          >
            수정
          </Button>
          <Popconfirm
            title="정말 삭제하시겠습니까?"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              삭제
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>학생 관리</h1>
        <Space>
          <Upload
            beforeUpload={handleUpload}
            accept=".xlsx,.xls,.csv"
            showUploadList={false}
          >
            <Button icon={<UploadOutlined />}>Excel 업로드</Button>
          </Upload>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingStudent(null);
              form.resetFields();
              setIsModalOpen(true);
            }}
          >
            학생 추가
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={students}
        rowKey="id"
        pagination={{ pageSize: 20 }}
      />

      <Modal
        title={editingStudent ? '학생 수정' : '학생 추가'}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          setEditingStudent(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
      >
        <Form form={form} onFinish={handleSave} layout="vertical">
          <Form.Item name="grade" label="학년" rules={[{ required: true }]}>
            <Input type="number" />
          </Form.Item>
          <Form.Item name="number" label="번호">
            <Input type="number" />
          </Form.Item>
          <Form.Item name="name" label="이름" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="gender" label="성별" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="남">남</Select.Option>
              <Select.Option value="여">여</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

