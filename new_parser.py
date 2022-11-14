from collections import defaultdict
from modified_brain import Brain, Area

# 我的命名逻辑：非终止符有谓词（pred）和指称词（deno）两种, 谓词根据变元数不同, 分为0, 1, 2, 3元等……
# 一个n元谓词可以填入一个指称词变为n-1元谓词
# 你可以有不同的命名逻辑, 如VP（替代谓词）, NP（替代指称词）等
# Area for stage 2 (components)
DET = "DET"
# 主语
SUBJ = "SUBJ"
# 指称词（专名）
DENO = "DENO"
ADJ = "ADJ"
PRED = "PRED"
PRED0 = "PRED0"
PRED1 = "PRED1"
PRED2 = "PRED2"
PRED3 = "PRED3"
ADV = "ADV"

# 全局最深的pred层数
max_pred_level = 3

# stage2
stage_2_Areas = {
    SUBJ: {},
    DENO: {},
    ADJ: {},
    PRED0: {},
    PRED1: {},
    PRED2: {},
    PRED3: {},
    ADV: {},
    DET: {}
}


# 取幂集, 生成正则表达式测试用例用的
def power_set(set1):
    ans = [[]]
    for i in set1:
        l = len(ans)
        for j in range(l):
            t = []
            t.extend(ans[j])
            t.append(i)
            ans.append(t)
    return ans


# 一部分参考代码, 可以在这个基础上完善
class ParserBrain(Brain):
    def __init__(self, p, lexeme_dict=None, all_areas=None, recurrent_areas=None, initial_areas=None,
                 readout_rules=None):
        Brain.__init__(self, p)

        if readout_rules is None:
            readout_rules = {}
        if initial_areas is None:
            initial_areas = []
        if recurrent_areas is None:
            recurrent_areas = []
        if all_areas is None:
            all_areas = []

        self.component_dict = {}
        self.all_areas = all_areas
        self.recurrent_areas = recurrent_areas
        self.initial_areas = initial_areas

        self.fiber_states = defaultdict()
        self.area_states = defaultdict(set)
        self.activated_fibers = defaultdict(set)
        self.readout_rules = readout_rules
        # self.initialize_states()

        self.lexeme_dict = lexeme_dict
        if lexeme_dict is None:
            self.generate_components()

    # 直接生成组件, 用于分步验证; area_index是在同类脑区中的index, area_name是真实name
    def generic_component(self, assembly_index, comp_name, n=1000, k=30, beta=0.1):
        area_name = comp_name + "_{}".format(len(stage_2_Areas[comp_name]))
        stage_2_Areas[comp_name].setdefault(len(stage_2_Areas[comp_name]), area_name)
        # 此时没有刺激, 只能从外部输入
        self.add_explicit_area(area_name, n, k, beta)
        area: Area = self.areas[area_name]
        # 返回的是Assembly对象
        return area.add_random_assembly(assembly_index)

    # 生成词库的方法
    # 可以参考original parser里的lexeme_dict
    def generate_components(self):
        # key: assembly_name
        COMP_DICT = {
            "the": self.generic_component("the", DET),
            "a": self.generic_component("a", DET),
            "dogs": self.generic_component("dogs", DENO),
            "cats": self.generic_component("cats", DENO),
            "mice": self.generic_component("mice", DENO),
            "city": self.generic_component("city", DENO),
            "chase": self.generic_component("chase", PRED2),
            "love": self.generic_component("love", PRED2),
            "bite": self.generic_component("bite", PRED2),
            "smart": self.generic_component("smart", ADJ),
            "big": self.generic_component("big", ADJ),
            "bad": self.generic_component("bad", ADJ),
            "run": self.generic_component("run", PRED1),
            "fly": self.generic_component("fly", PRED1),
            "quickly": self.generic_component("quickly", ADV),
            "rapidly": self.generic_component("rapidly", ADV),
            "usually": self.generic_component("usually", ADV),
            "I": self.generic_component("I", DENO),
            "you": self.generic_component("you", DENO),
            "saw": self.generic_component("saw", PRED2),
            "bring": self.generic_component("bring", PRED3),
            "banana": self.generic_component("banana", DENO),
        }
        self.component_dict = COMP_DICT

        for key, value in COMP_DICT.items():
            self.all_areas.append(value.area_name)

    # 生成测试用例,根据你的词表,生成所有合法的句子用于测试
    def generate_sentences(self, output_dir="test_sentences.txt"):
        # 以正则表达式"(Adj)*(Noun)(V)((Adj)*(Noun)+epsilon)"为例
        # 假设*不允许出现重复的字符
        output_list = []
        adj_list = []
        noun_list = []
        vt_list = []
        vi_list = []
        for key, value in self.component_dict.items():
            if ADJ in value.area_name:
                adj_list.append(key)
            elif DENO in value.area_name:
                noun_list.append(key)
            elif PRED1 in value.area_name:
                vi_list.append(key)
            elif PRED2 in value.area_name:
                vt_list.append(key)

        pow_adj = power_set(adj_list)
        # 生成名词词组
        np_list = []
        for noun in noun_list:
            for ap in pow_adj:
                np = ""
                for i in ap:
                    np += i + ' '
                np += noun
                np_list.append(np)
        # 组装句子
        for vt in vt_list:
            for i in np_list:
                for j in np_list:
                    output_list.append(i + ' ' + vt + ' ' + j)
        for vi in vi_list:
            for i in np_list:
                output_list.append(i + ' ' + vi)
        # 写文件
        with open(output_dir, "w") as f:
            for line in output_list:
                f.write(line + '\n')


if __name__ == '__main__':
    pb = ParserBrain(0.01)
    # 生成测试用例
    pb.generate_sentences()
    # 使用测试用例的时候如果数量太大可以随机抽部分
