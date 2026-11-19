"""Builds every chart and README visual from insurance.csv.   Run:  python scripts/build_visuals.py"""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.ticker import FuncFormatter
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
PL=os.path.join(ROOT,"Plots"); AS=os.path.join(ROOT,"assets")
for f in ["crosextra/Carlito-Regular.ttf","crosextra/Carlito-Bold.ttf","google-fonts/Poppins-Medium.ttf","google-fonts/Poppins-Bold.ttf"]:
    p="/usr/share/fonts/truetype/"+f
    if os.path.exists(p): fm.fontManager.addfont(p)
NAVY,TEAL,CORAL,AMBER,BLUE,INK,GREY="#0B2545","#13A89E","#E4572E","#F2A900","#2F80ED","#1F2937","#6B7280"
plt.rcParams.update({"font.family":"Carlito","font.size":12,"axes.edgecolor":"#CBD2DC","text.color":INK,"axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,
 "axes.spines.top":False,"axes.spines.right":False,"axes.titleweight":"bold","axes.titlesize":15,"axes.titlelocation":"left","axes.grid":True,"grid.color":"#E8ECF2","axes.axisbelow":True})
usd=FuncFormatter(lambda v,_:f"${v:,.0f}")
def save(fig,name,folder=PL,**k): fig.savefig(os.path.join(folder,name),dpi=170,bbox_inches="tight",facecolor="white",**k); plt.close(fig)

df=pd.read_csv(os.path.join(ROOT,"insurance.csv")).drop_duplicates().reset_index(drop=True)
df["smoker_l"]=df.smoker.map({"yes":"Smoker","no":"Non-smoker"}); PAL={"Smoker":CORAL,"Non-smoker":TEAL}
df["bmi_group"]=np.where(df.bmi<30,"BMI under 30","BMI 30 or more")
df["age_group"]=pd.cut(df.age,[18,30,40,50,65],right=False,labels=["18-29","30-39","40-49","50-64"])
s=df.smoker=="yes"; order=["Non-smoker","Smoker"]

# 01 distribution
fig,ax=plt.subplots(figsize=(10,4.6)); bins=np.linspace(0,64000,33)
ax.hist([df[~s].charges,df[s].charges],bins=bins,stacked=True,color=[TEAL,CORAL],label=["Non-smokers","Smokers"],edgecolor="white")
ax.axvline(df.charges.median(),color=NAVY,ls="--",lw=1.6); ax.axvline(df.charges.mean(),color=AMBER,ls="--",lw=1.6)
ax.text(df.charges.median()-400,ax.get_ylim()[1]*.92,f"Median ${df.charges.median():,.0f}",ha="right",color=NAVY,fontweight="bold")
ax.text(df.charges.mean()+400,ax.get_ylim()[1]*.80,f"Mean ${df.charges.mean():,.0f}",ha="left",color="#B07C00",fontweight="bold")
ax.set_title("Most people pay little, a few pay a lot, and the big bills are mostly smokers"); ax.set_xlabel("Annual insurance charges"); ax.set_ylabel("Number of customers"); ax.xaxis.set_major_formatter(usd); ax.legend(frameon=False)
save(fig,"01_charges_distribution.png")

# 02 correlation
c=df[["age","bmi","children","charges"]].corr(); fig,ax=plt.subplots(figsize=(6.2,4.8))
ax.imshow(c,cmap=matplotlib.colors.LinearSegmentedColormap.from_list("t",["#FFFFFF",TEAL]),vmin=0,vmax=1); ax.grid(False)
ax.set_xticks(range(4)); ax.set_yticks(range(4)); ax.set_xticklabels(["Age","BMI","Children","Charges"]); ax.set_yticklabels(["Age","BMI","Children","Charges"])
for i in range(4):
    for j in range(4): ax.text(j,i,f"{c.iloc[i,j]:.2f}",ha="center",va="center",fontsize=13,fontweight="bold",color="white" if c.iloc[i,j]>.6 else INK)
ax.set_title("Numbers alone only hint at the story"); save(fig,"02_correlation_heatmap.png")

# 03 smoking
fig,ax=plt.subplots(figsize=(10,4.2))
for i,k in enumerate(order):
    d=df[df.smoker_l==k].charges; ax.scatter(d,np.random.default_rng(1).normal(i,.07,len(d)),s=9,alpha=.35,color=PAL[k])
    ax.boxplot(d,positions=[i],vert=False,widths=.42,showfliers=False,patch_artist=True,boxprops=dict(facecolor="none",edgecolor=INK,lw=1.6),medianprops=dict(color=INK,lw=2.6),whiskerprops=dict(color=INK),capprops=dict(color=INK))
    ax.text(d.median(),i+.36,f"median ${d.median():,.0f}",ha="center",fontweight="bold",color=PAL[k])
ax.set_yticks([0,1]); ax.set_yticklabels([f"Non-smokers\n(n={(~s).sum():,})",f"Smokers\n(n={s.sum():,})"]); ax.set_ylim(-.6,1.7); ax.xaxis.set_major_formatter(usd); ax.set_xlabel("Annual insurance charges")
ax.set_title("Smokers pay 3.8x more on average (4.7x at the median)"); save(fig,"03_charges_by_smoking.png")

# 04 scatter BMI
fig,ax=plt.subplots(figsize=(10,5))
for k in order: d=df[df.smoker_l==k]; ax.scatter(d.bmi,d.charges,s=22,alpha=.6,color=PAL[k],label=k,edgecolor="white",linewidth=.3)
ax.axvline(30,color=GREY,ls=":",lw=1.5); ax.text(30.3,63000,"BMI 30",color=GREY,fontsize=11)
ax.set_xlabel("BMI"); ax.set_ylabel("Annual insurance charges"); ax.yaxis.set_major_formatter(usd); ax.legend(frameon=False,loc="upper left")
ax.set_title("Two clouds: smokers split into 'lower' and 'much higher' as BMI passes 30"); save(fig,"04_bmi_vs_charges_by_smoker.png")

# 05 interaction
g=df.groupby(["smoker_l","bmi_group"]).charges.mean().unstack(); n=df.groupby(["smoker_l","bmi_group"]).size().unstack()
fig,ax=plt.subplots(figsize=(8.4,4.6)); x=np.arange(2); w=.34
for j,(bg,col) in enumerate([("BMI under 30","#8ED6CF"),("BMI 30 or more",NAVY)]):
    vals=[g.loc[k,bg] for k in order]; ax.bar(x+(j-.5)*w,vals,w,color=col,label=bg)
    for xi,v,k in zip(x+(j-.5)*w,vals,order): ax.text(xi,v+700,f"${v:,.0f}\n(n={n.loc[k,bg]})",ha="center",fontsize=10.5,fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(["Non-smokers","Smokers"],fontsize=13); ax.yaxis.set_major_formatter(usd); ax.set_ylim(0,49000); ax.set_ylabel("Average annual charges"); ax.legend(frameon=False,loc="upper left")
ax.set_title("BMI barely matters for non-smokers, but doubles the bill for smokers"); save(fig,"05_smoking_and_bmi_interaction.png")

# 06 age
m=df.groupby(["age_group","smoker_l"],observed=True).charges.mean().unstack(); fig,ax=plt.subplots(figsize=(9.5,4.8))
for k in order: ax.plot(m.index.astype(str),m[k],marker="o",lw=3,ms=9,color=PAL[k],label=k)
for i,a in enumerate(m.index): ax.annotate(f"gap \\${m.loc[a,'Smoker']-m.loc[a,'Non-smoker']:,.0f}",(i,(m.loc[a,'Smoker']+m.loc[a,'Non-smoker'])/2),ha="center",fontsize=10.5,color=GREY,bbox=dict(boxstyle="round",fc="white",ec="#DDE3EA"))
ax.set_ylim(0,45000); ax.yaxis.set_major_formatter(usd); ax.set_xlabel("Age group"); ax.set_ylabel("Average annual charges"); ax.legend(frameon=False,loc="center right")
ax.set_title("Everyone pays more with age; the smoking gap stays near \\$23,000-\\$25,000"); save(fig,"06_age_and_smoking.png")

# 07 sex
fig,ax=plt.subplots(1,3,figsize=(12,4.2),gridspec_kw={"width_ratios":[1,1,1.2]})
sx=df.groupby("sex").charges.agg(["mean","median"]); x=np.arange(2)
ax[0].bar(x-.18,sx["mean"],.36,color=BLUE,label="Mean"); ax[0].bar(x+.18,sx["median"],.36,color="#9CC3F5",label="Median")
for xi,v in zip(list(x-.18)+list(x+.18),list(sx["mean"])+list(sx["median"])): ax[0].text(xi,v+250,f"${v:,.0f}",ha="center",fontsize=9.5)
ax[0].set_xticks(x); ax[0].set_xticklabels(["Female","Male"]); ax[0].yaxis.set_major_formatter(usd); ax[0].set_ylim(0,16500); ax[0].legend(frameon=False,fontsize=9); ax[0].set_title("1. Averages differ a little",fontsize=12)
sh=(pd.crosstab(df.sex,df.smoker,normalize="index")*100)["yes"]; ax[1].bar(["Female","Male"],sh.values,color=CORAL,width=.5,alpha=.9)
for xi,v in enumerate(sh.values): ax[1].text(xi,v+.5,f"{v:.1f}%",ha="center",fontweight="bold")
ax[1].set_ylim(0,30); ax[1].set_title("2. Men smoke more",fontsize=12); ax[1].yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%"))
sm=df.groupby(["sex","smoker_l"]).charges.mean().unstack()
for j,k in enumerate(order): ax[2].bar(x+(j-.5)*.36,[sm.loc["female",k],sm.loc["male",k]],.36,color=PAL[k],label=k)
for j,k in enumerate(order):
    for xi,sx_ in zip(x+(j-.5)*.36,["female","male"]): ax[2].text(xi,sm.loc[sx_,k]+500,f"${sm.loc[sx_,k]:,.0f}",ha="center",fontsize=9)
ax[2].set_xticks(x); ax[2].set_xticklabels(["Female","Male"]); ax[2].yaxis.set_major_formatter(usd); ax[2].set_ylim(0,38000); ax[2].legend(frameon=False,fontsize=9); ax[2].set_title("3. Split by smoking status",fontsize=12)
fig.suptitle("The sex 'gap' is mostly a smoking gap",x=.01,ha="left",fontsize=15,fontweight="bold"); fig.tight_layout(); save(fig,"07_sex_and_smoking.png")

# 08 children
ch=df.groupby("children").charges.agg(["count","median"]); fig,ax=plt.subplots(figsize=(8.6,4.4))
ax.bar(ch.index.astype(str),ch["median"],color=[TEAL if k<4 else "#B9C2CF" for k in ch.index],width=.65)
for i,(k,r) in enumerate(ch.iterrows()): ax.text(i,r["median"]+200,f"${r['median']:,.0f}\nn={int(r['count'])}",ha="center",fontsize=10)
ax.set_ylim(0,13500); ax.yaxis.set_major_formatter(usd); ax.set_xlabel("Number of children"); ax.set_ylabel("Median annual charges")
ax.set_title("No clear pattern by number of children (grey bars: very few customers)"); save(fig,"08_children.png")

# 09 region
fig,ax=plt.subplots(1,2,figsize=(11.5,4.4),gridspec_kw={"width_ratios":[1.2,1]})
ro=df.groupby("region").charges.median().sort_values().index.tolist()
ax[0].boxplot([df[df.region==r].charges for r in ro],vert=False,tick_labels=[r.title() for r in ro],showfliers=True,patch_artist=True,widths=.55,
  boxprops=dict(facecolor="#BFE8E4",edgecolor=NAVY),medianprops=dict(color=NAVY,lw=2.4),flierprops=dict(marker="o",ms=3,alpha=.4,mfc=GREY,mec="none"))
ax[0].xaxis.set_major_formatter(usd); ax[0].set_title("Charges look alike in every region",fontsize=13)
sr=(pd.crosstab(df.region,df.smoker,normalize="index")*100)["yes"].reindex(ro)
ax[1].barh([r.title() for r in ro],sr.values,color=[CORAL if r=="southeast" else "#F4B09C" for r in ro])
for i,v in enumerate(sr.values): ax[1].text(v+.3,i,f"{v:.1f}%",va="center",fontsize=10.5)
ax[1].set_xlim(0,30); ax[1].set_title("Share of smokers by region",fontsize=13); ax[1].xaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%"))
fig.tight_layout(); save(fig,"09_region.png")

# 10 share of costs
sc=df[s].charges.sum()/df.charges.sum()*100; fig,ax=plt.subplots(figsize=(10,3.3))
for yy,a in enumerate([sc,s.mean()*100]):
    ax.barh(yy,100-a,color=TEAL,height=.55); ax.barh(yy,a,left=100-a,color=CORAL,height=.55)
    ax.text((100-a)/2,yy,f"Non-smokers {100-a:.1f}%",ha="center",va="center",color="white",fontweight="bold"); ax.text(100-a/2,yy,f"Smokers {a:.1f}%",ha="center",va="center",color="white",fontweight="bold")
ax.set_yticks([0,1]); ax.set_yticklabels(["Total charges paid","Customers"]); ax.set_xlim(0,100); ax.set_xticks([]); ax.grid(False); ax.spines["bottom"].set_visible(False)
ax.set_title("1 in 5 customers generates about half of all costs"); save(fig,"10_smokers_share_of_costs.png")

# ---------------- ASSETS
W,H=1600,440; fig=plt.figure(figsize=(W/100,H/100),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(0,H); ax.axis("off")
ax.imshow(np.linspace(0,1,256).reshape(1,-1),extent=[0,W,0,H],aspect="auto",cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b",["#081B33","#0B2545","#0F4C5C"]),zorder=0)
px=1000+(df.bmi-15)/(54-15)*520; py=40+(df.charges/65000)*330
ax.scatter(px[~s],py[~s],s=9,c=TEAL,alpha=.7,linewidths=0,zorder=1); ax.scatter(px[s],py[s],s=11,c=CORAL,alpha=.85,linewidths=0,zorder=2)
ax.text(70,318,"What Really Drives the",fontsize=36,fontfamily="Poppins",fontweight="bold",color="white",va="center")
ax.text(70,262,"Price of Health Insurance?",fontsize=36,fontfamily="Poppins",fontweight="bold",color="#7FE3D9",va="center")
ax.text(72,200,"A friendly, data-driven look at 1,337 insurance customers",fontsize=20,fontfamily="Carlito",color="#CFE3FF",va="center")
for i,(t,cc) in enumerate([("Smoking",CORAL),("Age",AMBER),("BMI",TEAL),("Sex",BLUE),("Region",BLUE)]):
    xx=72+i*140; ax.add_patch(FancyBboxPatch((xx,95),124,38,boxstyle="round,pad=0,rounding_size=19",fc=cc,ec="none",zorder=3)); ax.text(xx+62,114,t,ha="center",va="center",fontsize=14,fontfamily="Poppins",fontweight="bold",color="#10213D" if cc==AMBER else "white",zorder=4)
ax.text(1000,16,"each dot = one customer  |  coral = smoker, teal = non-smoker",fontsize=11,color="#9DB8E3",zorder=3)
for k,(cc,w) in enumerate([(TEAL,.5),(AMBER,.3),(CORAL,.2)]): ax.add_patch(Rectangle((W*sum([.5,.3][:k]),0),W*w,10,fc=cc,ec="none",zorder=5))
fig.savefig(os.path.join(AS,"banner.png"),dpi=100); plt.close(fig)

kp=[("1,337","customers",NAVY),("$13,279","average yearly charge",TEAL),("$9,386","typical (median) charge",BLUE),("20.5%","are smokers",CORAL),("3.8x","smoker vs non-smoker cost",AMBER),("49.5%","of all costs come from smokers","#7A4EAB")]
fig=plt.figure(figsize=(16,1.9),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,1600); ax.set_ylim(0,190); ax.axis("off"); cw=250; gap=20; x0=(1600-(6*cw+5*gap))/2
for i,(v,l,cc) in enumerate(kp):
    x=x0+i*(cw+gap); ax.add_patch(FancyBboxPatch((x,15),cw,160,boxstyle="round,pad=0,rounding_size=14",fc="#F5F7FA",ec="#DDE3EA",lw=1.5)); ax.add_patch(Rectangle((x+14,15),cw-28,7,fc=cc,ec="none"))
    ax.text(x+cw/2,108,v,ha="center",va="center",fontsize=27,fontfamily="Poppins",fontweight="bold",color=cc); ax.text(x+cw/2,56,l,ha="center",va="center",fontsize=12.5,color="#374151")
fig.savefig(os.path.join(AS,"kpi_strip.png"),dpi=100,facecolor="white"); plt.close(fig)

fig=plt.figure(figsize=(16,.1),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,1600); ax.set_ylim(0,10); ax.axis("off")
for k,(cc,w) in enumerate([(TEAL,800),(AMBER,480),(CORAL,320)]): ax.add_patch(Rectangle((sum([800,480][:k]),0),w,10,fc=cc,ec="none"))
fig.savefig(os.path.join(AS,"divider.png"),dpi=100); plt.close(fig)

pg=df.groupby(["smoker","bmi_group"]).charges.agg(["count","median"])
P=[("The Baseline","Non-smoker, BMI under 30",pg.loc[("no","BMI under 30")],TEAL),("The Small Step Up","Non-smoker, BMI 30 or more",pg.loc[("no","BMI 30 or more")],"#3FB8B0"),
   ("The Smoker","Smoker, BMI under 30",pg.loc[("yes","BMI under 30")],AMBER),("The Double Factor","Smoker, BMI 30 or more",pg.loc[("yes","BMI 30 or more")],CORAL)]
fig=plt.figure(figsize=(16,4.4),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,1600); ax.set_ylim(0,440); ax.axis("off"); cw=370; gap=26; x0=(1600-(4*cw+3*gap))/2; mx=P[-1][2]["median"]
for i,(name,desc,r,cc) in enumerate(P):
    x=x0+i*(cw+gap); ax.add_patch(FancyBboxPatch((x,20),cw,390,boxstyle="round,pad=0,rounding_size=18",fc="#F7F9FC",ec="#DDE3EA",lw=1.6)); ax.add_patch(Rectangle((x+18,372),cw-36,8,fc=cc,ec="none"))
    ax.text(x+cw/2,335,name,ha="center",fontsize=21,fontfamily="Poppins",fontweight="bold",color=NAVY); ax.text(x+cw/2,298,desc,ha="center",fontsize=14,color=GREY)
    ax.text(x+cw/2,205,f"${r['median']:,.0f}",ha="center",va="center",fontsize=40,fontfamily="Poppins",fontweight="bold",color=cc); ax.text(x+cw/2,150,"typical yearly charge (median)",ha="center",fontsize=13,color="#374151")
    ax.add_patch(Rectangle((x+30,92),cw-60,16,fc="#E6EBF2",ec="none")); ax.add_patch(Rectangle((x+30,92),(cw-60)*r["median"]/mx,16,fc=cc,ec="none"))
    ax.text(x+cw/2,52,f"{int(r['count'])} customers",ha="center",fontsize=13,color=GREY)
fig.savefig(os.path.join(AS,"personas.png"),dpi=100,facecolor="white"); plt.close(fig)
print("ok")
