configfile : 'config.json'
data = '/data/' # wherever your data is stored

mapping = data + 'mapping.tsv'
snvs = data + 'sectionE.phased_snps_counts.pos.'
abcs = config['abcs']

m = 4 # largest value observed in distilled matrix
k = 63 # largest number of 1s observed in any row
ps = ['a{}.b{}'.format(a,b)
      for b in range(1,m+1)
      for a in range(1,b+1)]
clones = [63, 156, 172, 199, 241] # non-root clones from CN tree

time = '/usr/bin/time'
sasc = 'sasc/sasc'
threads = 16

patt = 'k{k}-a{a}-b{b}-sasc' # parameterization of sasc
ptwc = 'k{k,[0-9]+}-a{a,[0-9]+.[0-9]+}-b{b,[0-9]+.[0-9]+}-sasc'
sasf = 'k1-a0.1-b0.0001-sasc' # a particular parameterization

abcs = ['a{}.b{}.c{}'.format(a,b,c) for a,b,c in abcs]

#----------------------------------------------------------------------

rule master :
    input :
        expand(snvs + '{p}.mat.stats', p = ps),
        data + 'stats.csv',
        expand(snvs + '{abc}.sasc.' + sasf + '.out',
               abc = abcs),
        expand(snvs + '{abc}.clone{clone}.sasc.' + sasf + '.out',
               abc = abcs, clone = clones)

#----------------------------------------------------------------------

# run sasc on an input
rule sasc :
    input :
        pgrm = sasc,
        mat = '{path}.sasc.mat',
        snvs = '{path}.sasc.snvs.txt',
        cells = '{path}.sasc.cells.txt'

    output : '{path}.sasc.' + ptwc + '.out'

    log :
        log = '{path}.sasc.' + patt + '.log',
        time = '{path}.sasc.' + patt + '.time'

    threads : threads

    run :
        with open(input.mat) as mat :
            m = len(mat.readline().split())
            n = sum(1 for line in mat) + 1

        shell('''

  cp {input.mat} {output}.mat

  {time} -vo {log.time} \
    {sasc} -n {n} -m {m} -a {wildcards.a} -b {wildcards.b} \
      -k {wildcards.k} -l -x -p {threads} \
        -i {output}.mat -e {input.snvs} -E {input.cells} \
      > {output} 2> {log.log}

  rm {output}.mat ''')


# convert to sasc format
rule to_sasc :
    input : '{path}.mat'
    output :
        mat = '{path}.sasc.mat',
        snvs = '{path}.sasc.snvs.txt',
        cells = '{path}.sasc.cells.txt'

    log : '{path}.sasc.log'

    shell : '''

  head -1 {input} | awk '{{for(i=2;i<=NF;i++){{print $i}}}}' \
    > {output.cells} 2> {log}
  tail -n +2 {input} | cut -d' ' -f1 \
    > {output.snvs} 2>> {log}
  python3 scripts/to-sasc.py {input} \
    > {output.mat} 2>> {log} '''


# prepare the data
#----------------------------------------------------------------------

# split cells (columns) of a matrix into clones
rule split :
    input :
        mat = '{path}.mat',
        mapp = mapping

    output :
        expand('{{path}}.clone{clone}.mat', clone = clones)

    log : '{path}.split.log'

    shell : '''

  python3 scripts/split.py {input.mat} {input.mapp}
    > {log} 2>&1
  touch {output} '''


# keep rows above a certain threshold of number of ones
rule threshold :
    input : '{path}.mat'
    output : '{path}.c{c,[0-9]+}.mat'
    log : '{path}.c{c}.mat.log'
          
    shell : '''

  python3 scripts/threshold.py {input} {wildcards.c} \
    > {output} 2> {log} '''


# ternarize this smaller matrix format for different thresholds
rule ternarize :
    input : '{path}.mat'
    output : '{path}.a{a,[0-9]+}.b{b,[0-9]+}.mat'
    log : '{path}.a{a}.b{b}.mat.log'

    shell : '''

  python3 scripts/ternarize.py {input} {wildcards.a} {wildcards.b} \
    > {output} 2> {log} '''


# distill SNVs to smaller matrix format
rule distill :
    input :
        snv = '{path}.gz',
        mapp = mapping,
        sort_check = '{path}.sort_check', # sanity checks
        id_check = mapping + '.id_check'

    params :
        cells = 'None',
        mutations = '5'

    output : '{path}.mat.gz'
    log : '{path}.mat.log'

    shell : '''

  zcat {input.snv} \
    | python3 scripts/distill.py \
         -f {input.mapp} -c {params.cells} -m {params.mutations} \
    | gzip > {output} 2> {log} '''


# statistics, sanity checks
#----------------------------------------------------------------------

# gather stats
rule gather_stats :
    input :
        expand(data + 'sectionE.phased_snps_counts.pos.{p}.c{c}.mat.stats',
               p = ps, c = range(1,k+1))

    output : data + 'stats.csv'

    shell : '''

  echo "a,b,c,n,m,nxm,1s,?s,f1,f?" > {output}
  echo "---" >> {output}
  cat {input} | sort -t, -k1,1n -k2,2n -k3,3n >> {output} '''


# obtain some descriptive statistics of a matrix
rule mat_stats :
    input : '{path}.mat'
    output : '{path}.mat.stats'
    log : '{path}.mat.stats.log'
    shell : 'python3 scripts/mat-stats.py {input} > {output} 2> {log}'


# sanity check for sortedness of SNPs counts file
rule sort_check :
    input : '{path}.gz'
    output : '{path}.sort_check'
    shell : 'zcat {input} | sort -c -k1,1V -k2,2n > {output} 2>&1'


# sanity check for identity of cluster and clone
rule id_check :
    input : '{path}.tsv'
    output : '{path}.tsv.id_check'

    shell : '''

  grep -v "None" {input} \
    | sed 's/Clone//' \
    | awk '{{if($2!=$3){{print}}}}' > {output} 2>&1 '''


# sasc
#----------------------------------------------------------------------

# build sasc
rule build_sasc :
    input : 'sasc/README.md'
    output : sasc
    shell : '''

  cd sasc && make
  cd .. && touch {output} '''


# obtain sasc
rule get_sasc :
    output : 'sasc/README.md'
    shell : '''

  git clone https://github.com/sciccolella/sasc.git
  touch {output} '''
