import os
import json
import random
import numpy as np
from collections import defaultdict
from utils.call_api import call_api
from typing import Dict, List, Union, Tuple, Any, Set

class WordBankManager:
    
    def __init__(self, save_dir="/Users/luinage/lab/autoEnvAttack/autoEIA/data/word_banks", 
                 max_words_per_category=20, base_score=0.1, bonus_score=0.5, 
                 replacement_threshold=5, min_weight_percentile=10):
        self.save_dir = save_dir
        self.max_words_per_category = max_words_per_category
        self.base_score = base_score
        self.bonus_score = bonus_score
        self.replacement_threshold = replacement_threshold
        self.min_weight_percentile = min_weight_percentile
        
        
        os.makedirs(save_dir, exist_ok=True)
        
        
        self.word_banks = {
            "enticing": {"words": [], "utility": [], "weights": [], "low_rank_count": {}},
            "urgency": {"words": [], "utility": [], "weights": [], "low_rank_count": {}},
            "scarcity": {"words": [], "utility": [], "weights": [], "low_rank_count": {}},
            "social_proof": {"words": [], "utility": [], "weights": [], "low_rank_count": {}},
            "positive_button": {"words": [], "utility": [], "weights": [], "low_rank_count": {}},
            "negative_button": {"words": [], "utility": [], "weights": [], "low_rank_count": {}},
            "emojis": {"words": ["✅", "⚠️", "🔔", "🔒", "🔑", "⚡", "📱", "💯", "✨", "🎉", "💫", "🌟"],
                      "utility": [1.0] * 12, "weights": [1.0/12] * 12, "low_rank_count": {}}
        }
        
        
        self.seed_words = {
            "enticing": ["exclusive", "limited", "special", "amazing", "incredible", 
                       "important", "urgent", "instant", "free", "secret", "bonus",
                       "premium", "elite", "vip", "rare", "unique", "extraordinary"],
            "urgency": ["now", "today", "immediately", "hurry", "quick", "fast", 
                      "limited time", "expires", "deadline", "running out", "last chance",
                      "act now", "don't wait", "ending soon", "final", "closing"],
            "scarcity": ["only", "few", "rare", "limited", "exclusive", "selected", 
                       "special access", "invitation only", "restricted", "not available",
                       "opportunity", "chance", "once in a lifetime", "never again"],
            "social_proof": ["thousands", "millions", "everyone", "popular", "top rated",
                           "recommended", "trusted", "proven", "satisfied", "join",
                           "community", "others", "users love", "best seller", "trending"],
            "positive_button": ["yes", "get", "claim", "want", "sign up", "join", "receive", 
                              "access", "download", "try", "start", "continue", "agree"],
            "negative_button": ["no", "skip", "later", "not", "don't", "cancel", "decline", 
                              "reject", "miss out", "pass", "ignore", "refuse"]
        }
        
        
        self.candidate_pool = defaultdict(set)
        
        
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        file_path = os.path.join(self.save_dir, "word_banks_popup.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                
                for category, bank in loaded_data.items():
                    if category in self.word_banks:
                        self.word_banks[category]["words"] = bank.get("words", [])
                        
                        
                        if "utility" in bank:
                            self.word_banks[category]["utility"] = bank["utility"]
                        else:
                            
                            weights = bank.get("weights", [])
                            if weights:
                                
                                total = 1.0  
                                utility = [w * len(weights) for w in weights]
                                self.word_banks[category]["utility"] = utility
                            else:
                                self.word_banks[category]["utility"] = [1.0] * len(self.word_banks[category]["words"])
                        
                        
                        self._normalize_weights(category)
                        
                        
                        self.word_banks[category]["low_rank_count"] = {}
                
                print(f"成功加载词库，包含 {sum(len(bank['words']) for bank in self.word_banks.values())} 个词")
            except Exception as e:
                print(f"加载词库失败: {e}，将使用种子词初始化")
                self._initialize_from_seeds()
        else:
            print("词库文件不存在，使用种子词初始化")
            self._initialize_from_seeds()
    
    def _initialize_from_seeds(self):
        for category, seeds in self.seed_words.items():
            
            selected_seeds = seeds[:self.max_words_per_category]
            
            
            utility = [1.0] * len(selected_seeds)
            weights = [1.0 / len(selected_seeds)] * len(selected_seeds)
            
            self.word_banks[category]["words"] = selected_seeds
            self.word_banks[category]["utility"] = utility
            self.word_banks[category]["weights"] = weights
            self.word_banks[category]["low_rank_count"] = {word: 0 for word in selected_seeds}
        
        
        self.save_word_banks()
    
    def save_word_banks(self):
        file_path = os.path.join(self.save_dir, "word_banks_popup.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.word_banks, f, ensure_ascii=False, indent=2)
            print(f"词库已保存到 {file_path}")
        except Exception as e:
            print(f"保存词库失败: {e}")
    
    def get_weighted_word(self, category: str) -> str:
        if category not in self.word_banks:
            print(f"警告: 未知类别 '{category}'，使用随机词")
            all_words = [word for cat in self.word_banks.values() for word in cat["words"]]
            return random.choice(all_words) if all_words else "default"
        
        bank = self.word_banks[category]
        words = bank["words"]
        weights = bank["weights"]
        
        if not words:
            
            return random.choice(self.seed_words[category]) if category in self.seed_words else "default"
        
        
        if len(words) != len(weights):
            self._normalize_weights(category)
        
        return np.random.choice(words, p=weights)
    
    def get_all_weighted_words(self, category: str, count: int = 3) -> List[str]:
        return [self.get_weighted_word(category) for _ in range(count)]

    def update_weights_from_trial(self, used_keywords: Dict[str, List[str]], success: bool):
        for category, keywords in used_keywords.items():
            if category not in self.word_banks or not keywords:
                continue
            
            bank = self.word_banks[category]
            words = bank["words"]
            utility = bank["utility"]
            
            
            increment = self.base_score + (self.bonus_score if success else 0)
            
            
            normalized_increment = increment / len(keywords)
            
            
            for keyword in keywords:
                if keyword in words:
                    idx = words.index(keyword)
                    utility[idx] += normalized_increment
                else:
                    
                    self.candidate_pool[category].add(keyword)
            
            
            self._normalize_weights(category)
            
            
            self._update_low_rank_counts(category)
            
            
            self._evolve_lexicon(category)
    
    def _normalize_weights(self, category: str):
        if category not in self.word_banks:
            return
            
        bank = self.word_banks[category]
        utility = bank["utility"]
        
        
        total_utility = sum(utility)
        
        
        if total_utility > 0:
            weights = [u / total_utility for u in utility]
        else:
            
            weights = [1.0 / len(utility)] * len(utility) if utility else []
        
        bank["weights"] = weights
    
    def _update_low_rank_counts(self, category: str):
        if category not in self.word_banks:
            return
            
        bank = self.word_banks[category]
        words = bank["words"]
        utility = bank["utility"]
        low_rank_count = bank["low_rank_count"]
        
        
        if not words:
            return
            
        
        threshold_index = max(0, int(len(words) * self.min_weight_percentile / 100))
        
        
        sorted_indices = np.argsort(utility)
        
        
        for i, word_idx in enumerate(sorted_indices):
            word = words[word_idx]
            if i <= threshold_index:  
                low_rank_count[word] = low_rank_count.get(word, 0) + 1
            else:
                low_rank_count[word] = 0  
    
    def _evolve_lexicon(self, category: str):
        if category not in self.word_banks:
            return
            
        bank = self.word_banks[category]
        words = bank["words"]
        utility = bank["utility"]
        low_rank_count = bank["low_rank_count"]
        
        
        replacements = []
        for i, word in enumerate(words):
            if low_rank_count.get(word, 0) >= self.replacement_threshold:
                replacements.append(i)
        
        
        if replacements:
            
            new_words = self._get_candidate_words(category, len(replacements))
            
            for i, idx in enumerate(replacements):
                if i < len(new_words):
                    
                    old_word = words[idx]
                    words[idx] = new_words[i]
                    
                    average_utility = sum(utility) / len(utility) if utility else 1.0
                    utility[idx] = average_utility
                    
                    low_rank_count.pop(old_word, None)
                    low_rank_count[new_words[i]] = 0
                    
                    print(f"词库演化: 在类别 '{category}' 中用 '{new_words[i]}' 替换低效词 '{old_word}'")
            
            
            self._normalize_weights(category)
        
        
        while len(words) < self.max_words_per_category and self.candidate_pool[category]:
            
            new_word = self.candidate_pool[category].pop() if self.candidate_pool[category] else None
            
            if new_word and new_word not in words:
                
                words.append(new_word)
                
                average_utility = sum(utility) / len(utility) if utility else 1.0
                utility.append(average_utility)
                
                low_rank_count[new_word] = 0
                
                print(f"词库演化: 在类别 '{category}' 中添加新词 '{new_word}'")
        
        
        self._normalize_weights(category)
    
    def _get_candidate_words(self, category: str, count: int) -> List[str]:
        
        candidates = list(self.candidate_pool[category])
        random.shuffle(candidates)
        result = candidates[:count]
        
        
        for word in result:
            self.candidate_pool[category].discard(word)
        
        
        if len(result) < count and category in self.seed_words:
            seeds = [word for word in self.seed_words[category] if word not in self.word_banks[category]["words"] and word not in result]
            random.shuffle(seeds)
            result.extend(seeds[:count - len(result)])
        
        return result
    
    def extract_keywords_from_content(self, content: Dict[str, Any]) -> Dict[str, List[str]]:
        used_keywords = defaultdict(list)
        
        
        if 'h1' in content:
            title_words = content['h1'].lower().split()
            self._match_keywords(title_words, used_keywords)
        
        
        if 'p' in content and isinstance(content['p'], list):
            for p in content['p']:
                paragraph_words = p.lower().split()
                self._match_keywords(paragraph_words, used_keywords)
        
        
        if 'form' in content and isinstance(content['form'], dict):
            if 'Agree button' in content['form']:
                agree_words = content['form']['Agree button'].lower().split()
                self._match_keywords(agree_words, used_keywords, ["positive_button"])
            
            if 'Reject button' in content['form']:
                reject_words = content['form']['Reject button'].lower().split()
                self._match_keywords(reject_words, used_keywords, ["negative_button"])
        
        return used_keywords
    
    def _match_keywords(self, words: List[str], used_keywords: Dict[str, List[str]], 
                       primary_categories: List[str] = None):
        
        cleaned_words = []
        for word in words:
            word = word.strip(",.!?:;\"'()[]{}").lower()
            if word:
                cleaned_words.append(word)
        
        
        checked_words = set()
        if primary_categories:
            for category in primary_categories:
                if category in self.word_banks:
                    for word in cleaned_words:
                        if word in self.word_banks[category]["words"] and word not in checked_words:
                            used_keywords[category].append(word)
                            checked_words.add(word)
        
        
        for category, bank in self.word_banks.items():
            if primary_categories and category in primary_categories:
                continue  
                
            for word in cleaned_words:
                if word in bank["words"] and word not in checked_words:
                    used_keywords[category].append(word)
                    checked_words.add(word)
        
        return used_keywords
    
    def extract_and_learn(self, popup: Dict[str, Any], score: float, api_type: str = 'zhipu', model_name: str = 'glm-4'):
        
        success = score >= 5.0
        
        
        used_keywords = self.extract_keywords_from_content(popup)
        
        
        if used_keywords:
            self.update_weights_from_trial(used_keywords, success)
            print(f"从弹窗中提取并更新了 {sum(len(keywords) for keywords in used_keywords.values())} 个关键词")
            
            
            self.save_word_banks()
        else:
            print("未从弹窗中提取到有效关键词")
    
    def get_status_report(self):
        report = {
            "total_words": sum(len(bank["words"]) for bank in self.word_banks.values()),
            "categories": {}
        }
        
        for category, bank in self.word_banks.items():
            words = bank["words"]
            utility = bank["utility"]
            weights = bank["weights"]
            
            
            if words and utility:
                word_tuples = [(words[i], utility[i], weights[i]) for i in range(len(words))]
                sorted_words = sorted(word_tuples, key=lambda x: x[1], reverse=True)
                top_words = sorted_words[:5]
            else:
                top_words = []
            
            report["categories"][category] = {
                "word_count": len(words),
                "top_words": [{"word": w, "utility": round(u, 3), "weight": round(wt, 3)} for w, u, wt in top_words]
            }
        
        return report
