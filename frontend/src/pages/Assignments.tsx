import { useEffect, useState } from 'react';
import {
  Button,
  Table,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  message,
  Card,
  Statistic,
  Row,
  Col,
  Popconfirm,
  Progress,
} from 'antd';
import { PlusOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useStore } from '../store/useStore';
import { assignmentApi } from '../api';
import type { Assignment, AssignmentDetail } from '../types';

export const Assignments = () => {
  const { currentSchool, assignments, setAssignments, setLoading } = useStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<AssignmentDetail | null>(null);
  const [form] = Form.useForm();
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (currentSchool) {
      loadAssignments();
    }
  }, [currentSchool]);

  const loadAssignments = async () => {
    if (!currentSchool) return;

    try {
      setLoading(true);
      const response = await assignmentApi.getAll(currentSchool.id);
      setAssignments(response.data);
    } catch (error) {
      message.error('반편성 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (values: any) => {
    try {
      setGenerating(true);
      await assignmentApi.generate({
        school_id: currentSchool!.id,
        ...values,
      });
      message.success('반편성이 완료되었습니다!');
      setIsModalOpen(false);
      form.resetFields();
      loadAssignments();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '반편성에 실패했습니다.');
    } finally {
      setGenerating(false);
    }
  };

  const handleViewDetail = async (id: number) => {
    try {
      setLoading(true);
      const response = await assignmentApi.getById(id);
      setSelectedAssignment(response.data);
      setIsDetailModalOpen(true);
    } catch (error) {
      message.error('상세 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setLoading(true);
      await assignmentApi.delete(id);
      message.success('반편성이 삭제되었습니다.');
      loadAssignments();
    } catch (error) {
      message.error('삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const columns: ColumnsType<Assignment> = [
    { title: '이름', dataIndex: 'name', key: 'name' },
    { title: '학년', dataIndex: 'grade', key: 'grade', width: 80 },
    { title: '연도', dataIndex: 'year', key: 'year', width: 100 },
    { title: '반 개수', dataIndex: 'num_classes', key: 'num_classes', width: 100 },
    {
      title: '점수',
      dataIndex: 'total_score',
      key: 'total_score',
      width: 120,
      render: (score) => score ? `${score.toFixed(2)}점` : '-',
    },
    {
      title: '작업',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EyeOutlined />} onClick={() => handleViewDetail(record.id)}>
            상세
          </Button>
          <Popconfirm title="정말 삭제하시겠습니까?" onConfirm={() => handleDelete(record.id)}>
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
        <h1>반편성</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            form.resetFields();
            setIsModalOpen(true);
          }}
        >
          새 반편성
        </Button>
      </div>

      <Table columns={columns} dataSource={assignments} rowKey="id" />

      <Modal
        title="새 반편성 생성"
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        confirmLoading={generating}
      >
        <Form 
          form={form} 
          onFinish={handleGenerate} 
          layout="vertical"
          initialValues={{ method: 'genetic', iterations: 1000, year: new Date().getFullYear() }}
        >
          <Form.Item name="name" label="이름" rules={[{ required: true }]}>
            <Input placeholder="예: 2024년 3학년 1학기" />
          </Form.Item>
          <Form.Item name="grade" label="학년" rules={[{ required: true }]}>
            <InputNumber min={1} max={6} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="year" label="연도" rules={[{ required: true }]}>
            <InputNumber min={2020} max={2030} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="num_classes" label="반 개수" rules={[{ required: true }]}>
            <InputNumber min={1} max={20} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="method" label="알고리즘" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="random">무작위</Select.Option>
              <Select.Option value="greedy">탐욕</Select.Option>
              <Select.Option value="genetic">유전 (권장)</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="iterations" label="반복 횟수">
            <InputNumber min={100} max={5000} step={100} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
        {generating && (
          <div style={{ marginTop: 16 }}>
            <Progress percent={100} status="active" />
            <p style={{ textAlign: 'center', marginTop: 8 }}>반편성 진행 중...</p>
          </div>
        )}
      </Modal>

      <Modal
        title="반편성 상세"
        open={isDetailModalOpen}
        onCancel={() => setIsDetailModalOpen(false)}
        footer={null}
        width={800}
      >
        {selectedAssignment && (
          <div>
            <Card title="전체 통계" style={{ marginBottom: 16 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic title="총점" value={selectedAssignment.assignment.total_score?.toFixed(2)} suffix="점" />
                </Col>
                <Col span={8}>
                  <Statistic title="전체 학생" value={selectedAssignment.assignment.statistics.total_students} suffix="명" />
                </Col>
                <Col span={8}>
                  <Statistic title="반 개수" value={selectedAssignment.assignment.num_classes} suffix="개" />
                </Col>
              </Row>
            </Card>

            <Card title="규칙별 점수" style={{ marginBottom: 16 }}>
              {Object.entries(selectedAssignment.assignment.rule_scores).map(([name, score]) => (
                <div key={name} style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{name}</span>
                    <span>{score.toFixed(2)}점</span>
                  </div>
                  <Progress percent={score} showInfo={false} />
                </div>
              ))}
            </Card>

            <Card title="반별 구성">
              {Object.entries(selectedAssignment.classes).map(([classNum, students]) => (
                <div key={classNum} style={{ marginBottom: 16 }}>
                  <h4>{classNum}반 ({students.length}명)</h4>
                  <div>
                    남: {students.filter(s => s.gender === '남').length}명, 
                    여: {students.filter(s => s.gender === '여').length}명
                  </div>
                </div>
              ))}
            </Card>
          </div>
        )}
      </Modal>
    </div>
  );
};

