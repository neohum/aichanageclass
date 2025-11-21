import { useEffect, useState } from 'react';
import {
  Button,
  Table,
  Space,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  message,
  Popconfirm,
  Tag,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useStore } from '../store/useStore';
import { ruleApi } from '../api';
import type { Rule } from '../types';

export const Rules = () => {
  const { currentSchool, rules, setRules, setLoading } = useStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [form] = Form.useForm();
  const [ruleType, setRuleType] = useState<string>('balance');

  useEffect(() => {
    if (currentSchool) {
      loadRules();
    }
  }, [currentSchool]);

  const loadRules = async () => {
    if (!currentSchool) return;

    try {
      setLoading(true);
      const response = await ruleApi.getAll(currentSchool.id);
      setRules(response.data);
    } catch (error) {
      message.error('규칙 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: any) => {
    try {
      setLoading(true);
      
      // rule_definition 구성
      const ruleDefinition = {
        type: values.rule_type,
        field: values.field,
        ...values,
      };

      const ruleData = {
        school_id: currentSchool?.id,
        name: values.name,
        description: values.description,
        rule_type: values.rule_type,
        priority: values.priority,
        weight: values.weight,
        rule_definition: ruleDefinition,
        is_active: values.is_active ?? true,
      };

      if (editingRule) {
        await ruleApi.update(editingRule.id, ruleData);
        message.success('규칙이 수정되었습니다.');
      } else {
        await ruleApi.create(ruleData);
        message.success('규칙이 추가되었습니다.');
      }

      setIsModalOpen(false);
      form.resetFields();
      setEditingRule(null);
      loadRules();
    } catch (error) {
      message.error('저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setLoading(true);
      await ruleApi.delete(id);
      message.success('규칙이 삭제되었습니다.');
      loadRules();
    } catch (error) {
      message.error('삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (id: number) => {
    try {
      await ruleApi.toggle(id);
      loadRules();
    } catch (error) {
      message.error('상태 변경에 실패했습니다.');
    }
  };

  const handleEdit = (rule: Rule) => {
    setEditingRule(rule);
    setRuleType(rule.rule_type);
    form.setFieldsValue({
      ...rule,
      ...rule.rule_definition,
    });
    setIsModalOpen(true);
  };

  const columns: ColumnsType<Rule> = [
    { title: '이름', dataIndex: 'name', key: 'name' },
    { 
      title: '유형', 
      dataIndex: 'rule_type', 
      key: 'rule_type',
      render: (type) => {
        const colors: Record<string, string> = {
          balance: 'blue',
          constraint: 'orange',
          distribution: 'green',
          complex: 'purple',
        };
        return <Tag color={colors[type]}>{type}</Tag>;
      }
    },
    { title: '우선순위', dataIndex: 'priority', key: 'priority', width: 100 },
    { title: '가중치', dataIndex: 'weight', key: 'weight', width: 100 },
    {
      title: '상태',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (active, record) => (
        <Switch checked={active} onChange={() => handleToggle(record.id)} />
      ),
    },
    {
      title: '작업',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            수정
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
        <h1>규칙 설정</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditingRule(null);
            form.resetFields();
            setRuleType('balance');
            setIsModalOpen(true);
          }}
        >
          규칙 추가
        </Button>
      </div>

      <Table columns={columns} dataSource={rules} rowKey="id" />

      <Modal
        title={editingRule ? '규칙 수정' : '규칙 추가'}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          setEditingRule(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        width={600}
      >
        <Form form={form} onFinish={handleSave} layout="vertical" initialValues={{ priority: 5, weight: 1.0 }}>
          <Form.Item name="name" label="규칙 이름" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="설명">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="rule_type" label="규칙 유형" rules={[{ required: true }]}>
            <Select onChange={setRuleType}>
              <Select.Option value="balance">균형 규칙</Select.Option>
              <Select.Option value="constraint">제약 규칙</Select.Option>
              <Select.Option value="distribution">분산 규칙</Select.Option>
            </Select>
          </Form.Item>

          {ruleType === 'balance' && (
            <>
              <Form.Item name="field" label="필드" rules={[{ required: true }]}>
                <Input placeholder="예: gender, 성적" />
              </Form.Item>
              <Form.Item name="target" label="목표" rules={[{ required: true }]}>
                <Select>
                  <Select.Option value="equal">동일</Select.Option>
                  <Select.Option value="average">평균</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item name="tolerance" label="허용 오차" rules={[{ required: true }]}>
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </>
          )}

          {ruleType === 'distribution' && (
            <>
              <Form.Item name="field" label="필드" rules={[{ required: true }]}>
                <Input placeholder="예: 특별관리, 리더십점수" />
              </Form.Item>
              <Form.Item name="strategy" label="전략" rules={[{ required: true }]}>
                <Select>
                  <Select.Option value="spread">분산</Select.Option>
                  <Select.Option value="limit">제한</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item name="max_per_class" label="반당 최대 인원">
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
            </>
          )}

          <Form.Item name="priority" label="우선순위 (1-10)" rules={[{ required: true }]}>
            <InputNumber min={1} max={10} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="weight" label="가중치" rules={[{ required: true }]}>
            <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

