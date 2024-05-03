import re
from typing import List
import argparse

def text_to_stitches(text: str, punc_spaces: int=2, zero_as_punctuation: bool=True):
    stitches = ''
    
    for char in text.lower():
        
        if re.match(r'\s+', char):
            # all whitespace characters are 1:1 knit stitches
            stitches += 'k'
            
        elif re.match(r'\d+', char):
            # treates 0 as punctuation if flag is set
            if zero_as_punctuation and char == '0':
                    stitches += 'p'*punc_spaces + 'k'

            # all other digits are 1:1 purl stitches
            stitches += 'p' * int(char) + 'k'
            
        elif re.match(r'\w+', char):
            # all letters are 1:1 purl stitches
            stitches += 'p'

        else:
            # catchall, everything else is treated as punctuation and is 1:2 knit stitches
            stitches += 'k' * punc_spaces
            
    return stitches

def fix_long_repeats(string: str, 
                     max_purl_run_len: int=12, 
                     max_knit_run_len: int=2, 
                     purl_run_spacer_char: str='k'): 
    
    # Fix long purl runs
    pattern = r'(p)\1{' + str(max_purl_run_len) + r',}'
    matches = re.finditer(pattern, string)
    start_ixs = [match.start() for match in matches]
    
    for ix in start_ixs:
        string = string[:ix+max_purl_run_len] + purl_run_spacer_char + string[ix+max_purl_run_len:]
        
    # Fix long knit runs
    pattern = r'k{' + str(max_knit_run_len+1) + r',}'
    string = re.sub(pattern, 'k' * int(max_knit_run_len), string)
        
    return string


def break_sequence(sequence: str, grouping_size: int=10): 
    return [sequence[i:i+grouping_size] for i in range(0, len(sequence), grouping_size)]

def consolidate_sequence_into_pattern(sequence: str):
    consolidated = ''
    current = sequence[0]
    count = 1

    for stitch in sequence[1:]:
        if stitch == current:
            count += 1
        else:
            consolidated += (current + str(count) + ' ')
            current = stitch
            count = 1
    
    consolidated += (current + str(count) + ' ')
    
    return consolidated

def consolidate_sequences(sequences: List[str]):
    pattern = []
    for s in sequences:
        pattern.append(consolidate_sequence_into_pattern(s))
        
    return '\n'.join(pattern)

def text_to_knitting(text: str, 
                     stitches_per_line: int=10, 
                     max_purl_run_len: int=12, 
                     max_knit_run_len: int=2, 
                     purl_run_spacer_char: str='k', 
                     punctuation_mapping: int=2, 
                     treat_zero_as_punctuation: bool=True
                     ):
    
    stitches = text_to_stitches(text, 
                                punc_spaces=punctuation_mapping, 
                                zero_as_punctuation=treat_zero_as_punctuation
                                )
    
    stitches = fix_long_repeats(stitches, 
                                max_purl_run_len=max_purl_run_len, 
                                max_knit_run_len=max_knit_run_len,
                                purl_run_spacer_char=purl_run_spacer_char)
    
    stitch_groups = break_sequence(stitches, grouping_size=stitches_per_line)
    
    pattern = consolidate_sequences(stitch_groups)
    
    return pattern


def divide_original_text(text: str, grouping_size: int=10):
    return '\n'.join([text[i:i+grouping_size] for i in range(0, len(text), grouping_size)]).strip()

test_text = 'test helloworldsofwater how are you doing today 2024-05-03?'


if __name__ == '__main__':
    
    argparser = argparse.ArgumentParser(description='Convert text to knitting pattern')
    argparser.add_argument('--text', type=str, default=test_text, help='Text to convert to knitting pattern')
    argparser.add_argument('--stitches_per_line', type=int, default=10, help='Number of stitches per line')
    argparser.add_argument('--max_purl_run_len', type=int, default=12, help='Maximum length of purl run before inserting spacer')
    argparser.add_argument('--max_knit_run_len', type=int, default=2, help='Maximum length of knit run before shortening')
    argparser.add_argument('--purl_run_spacer_char', type=str, default='k', help='Character to insert between purl runs')
    argparser.add_argument('--punctuation_mapping', type=int, default=2, help='Number of knit stitches to use for punctuation')
    argparser.add_argument('--treat_zero_as_punctuation', type=bool, default=True, help='Treat 0 as punctuation')
    
    pattern = text_to_knitting(**vars(argparser.parse_args()))    
    print(pattern)
        
    
